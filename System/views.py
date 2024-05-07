import os
from openai import OpenAI
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY", ""),
)


# 当settings.py的DEBUG为True时, 该视图函数不会被调用, 因为Django要暴露错误信息以方便开发者调试
def custom_404_interceptor(request, exception): # 该视图函数用于无效页面的重定向
    return redirect('User:login')

def copilot(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')

        prompt_template = """
        You are Watson, a knowledgeable assistant for a system called "Mrs. Hudson". 
        Mrs. Hudson is a comprehensive resource manager for exhibition centers to minimize waste and optimize asset and energy usage. 
        A user is asking for help, and you need to provide clear, concise, and helpful information. 
        
        Please provide a clear and detailed response.
        """
        
        if user_input:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages= [
                    {
                        "role": "system",
                        "content": prompt_template
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                max_tokens=250
            )
            chat_response = response.choices[0].message.content
            
            return render(request, 'System/copilot.html', {'response': chat_response, 'user_input': user_input})


    # Handle GET request or empty POST request
    return render(request, 'System/copilot.html')
