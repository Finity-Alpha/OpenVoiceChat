import queue


class BaseChatbot:
    def __init__(self):
        """
        Initialize the model and other things here
        """

    def run(self, input_text: str):
        """
        Yields the response to the input text
        """
        raise NotImplementedError("This method should be implemented by the subclass")

    def post_process(self, response: str) -> str:
        """
        Post process the response before returning
        """
        return response

    def generate_response(self, input_text: str) -> str:
        """
        :param input_text: The user input
        :return: The chatbot's response.
        """
        out = self.run(input_text)
        response_text = ""
        for o in out:
            text = o
            response_text += text
        response = self.post_process(response_text)
        return response

    def generate_response_stream(
        self, input_text: str, output_queue: queue.Queue, interrupt_queue: queue.Queue
    ) -> str:
        """
        :param input_text: The user input
        :param output_queue: The text output queue where the result is accumulated.
        :param interrupt_queue: The interrupt queue which stores the transcription if interruption occurred. Used to stop generating.
        :return: The chatbot's response after running self.post_process
        """
        out = self.run(input_text)
        response_text = ""
        for text in out:
            if not interrupt_queue.empty():
                break
            output_queue.put(text)
            response_text += text
        output_queue.put(None)
        response = self.post_process(response_text)
        return response
