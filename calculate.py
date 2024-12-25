#import tiktoken
import tiktoken
import json

# Open and read the JSON file
with open('pricing_data.json', 'r') as file:
    data = json.load(file)


class calculator():

    def __init__(self, providers, models):
        # self.in_token = 0
        # self.out_token = 0
        self.providers = providers
        self.models = models

    
    def count_from_text(self,input):

        encoding = tiktoken.get_encoding("cl100k_base")
        input_tokens = len(encoding.encode(input))
        #output_tokens = len(encoding.encode(output))
        return input_tokens
    

    def calculate(self, input_tokens, output_tokens):

        input_cost, output_cost = data[self.providers][self.models]
        input_cost_per_token = input_cost/1000000
        output_cost_per_token = output_cost/1000000

        total_cost = (input_cost_per_token * input_tokens) + (output_cost_per_token * output_tokens)

        return round(total_cost, 10)