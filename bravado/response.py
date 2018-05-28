# -*- coding: utf-8 -*-


class BravadoResponse(object):
    def __init__(self, incoming_response, result):
        self.incoming_response = incoming_response
        self.result = result
        self.response_metadata = BravadoResponseMetadata(
            incoming_response=self.incoming_response,
            swagger_result=self.result,
        )


class BravadoResponseMetadata(object):
    def __init__(self, incoming_response, swagger_result):
        self.incoming_response = incoming_response
        self.swagger_result = swagger_result
