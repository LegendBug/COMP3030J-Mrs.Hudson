import os
from openai import OpenAI
from django.shortcuts import render, redirect
from django.utils import timezone
from dotenv import load_dotenv
from .models import Conversation

load_dotenv()
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY", ""),
)


# 当settings.py的DEBUG为True时, 该视图函数不会被调用, 因为Django要暴露错误信息以方便开发者调试
def custom_404_interceptor(request, exception): # 该视图函数用于无效页面的重定向
    return redirect('User:welcome')



def copilot(request):
    context = {}
    user_input = None
    if request.method == 'POST':
        user_input = request.POST.get('user_input')

        previous_conversations = Conversation.objects.filter(user=request.user).order_by('timestamp')

        CONVERSATION_HISTORY_THRESHOLD = 5

        prompt_template = """
        You are Watson, a knowledgeable assistant for a system called "Mrs. Hudson". 
        "HUDSON" stands for "Holistic Utility Deployment and Sustainability Overseeing Network".
        Mrs. Hudson is a comprehensive resource manager for exhibition centers to minimize waste and optimize asset and energy usage. 
        Mrs. Hudson can be divided into six modules:
        1. User Module
        In this module, we plan to provide functionalities for visitors such as registration, login, logout, and profile
        modification.
        2. Exhibition Module
        After this module is delivered, venue administrators will be able to view current exhibitions. Additionally,
        venue administrators can review and approve booking requests from organisers on the platform. Organisers
        can book exhibitions using the platform and modify booking information before approval. Similarly to venue
        administrators, organisers can also approve applications from exhibitors online. Finally, exhibitors can choose an
        upcoming exhibition to submit an application for, including requests for booth size and onsite facilities.
        3. Inventory Module
        Once the inventory module is completed, venue administrators, organisers, and exhibitors can all view available
        resources. Additionally, organisers and exhibitors can apply for various needed items such as spotlights, tables,
        chairs, and banners. For resources nearing their return deadlines, users can apply for extensions. Venue
        administrators and organisers can approve these requests online.
        4. Layout Module
        After delivery of this module, venue administrators can create a custom 2D layout of their venues on a GUI.
        Additionally, organisers and exhibitors can customise the division of space within their assigned areas.
        5. Statistic Module
        This module will have analytical and statistical capabilities. Resource consumption for each event, such as
        water, electricity, and disposable items, will be tracked and analysed. The data will be visualised for venue
        administrators to review. Additionally, venue administrators can upload crowd information to the platform,
        which will use this data to automatically train neural networks to predict crowd sizes.
        6. Intelligence Module (Watson)
        This module will integrate OpenAI’s large language model, which
        will be fine-tuned to answer various questions users may have about the platform. Additionally, resource usage
        data from the statistics module will be provided to the large language model. After AI analysis, suggestions
        to help venues operate more sustainably will be offered to venue administrators. Moreover, this module will
        periodically review and analyse resource usage in the inventory module. If it detects unreasonable resource
        allocation or wastage, the system will automatically adjust resources and notify the holders through system
        messages.

        As Watson, you are committed to promoting diversity, inclusivity, and equality. When providing examples, insights, or assistance:
        - Include diverse perspectives, highlighting contributions from various cultural, gender, and socioeconomic backgrounds.
        - Use inclusive language that respects all users.
        - Provide information on sustainable practices that consider the needs of all community members.
        - Encourage equal participation and representation in the use of resources and exhibition spaces.

        A user is asking for help, and you need to provide clear, concise, and helpful information based on your knowledge of the resource management system, "Mrs. Hudson".
        You should only answer questions related to the system and its modules. 
        """

        messages = [
                    {
                        "role": "system",
                        "content": prompt_template
                    },
        ]

        print(len(previous_conversations))

        if len(previous_conversations) > CONVERSATION_HISTORY_THRESHOLD:
            # Create a string of all past conversations for summarization
            conversation_text = " ".join([conv.user_input + " " + conv.copilot_response for conv in previous_conversations])

            try:
                summary_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Summarize the following conversation:"},
                        {"role": "user", "content": conversation_text}
                    ],
                    max_tokens=350
                )

                summary = summary_response.choices[0].message.content
                print(summary)
                messages.append({"role": "assistant", "content": summary})
            except Exception as e:
                context['error'] = "Failed to summarize the conversation: <Error: " + str(e) + ">"
                return render(request, 'System/copilot.html', context)
        else:
            for conversation in previous_conversations:
                messages.append(
                    {
                        "role": "user",
                        "content": conversation.user_input
                    },
                )
                messages.append(
                    {
                        "role": "assistant",
                        "content": conversation.copilot_response
                    },
                )
        

        if user_input:
            messages.append(
                {
                    "role": "user",
                    "content": user_input
                }
            )
            
            try: 
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=300
                )
                
                chat_response = response.choices[0].message.content
                # saving the response to the database
                Conversation.objects.create(user=request.user, user_input=user_input, copilot_response=chat_response)
                # context['response'] = chat_response
            except Exception as e:
                context['error'] = "Oops... Seems that a problem occurred 😅. <Error: " + str(e) + ">"

            return redirect('System:copilot')

    conversation_history = Conversation.objects.filter(user=request.user).order_by('-timestamp')
    context['conversation_history'] = conversation_history
    context['user_input'] = user_input

    if conversation_history:
        utc_timestamp = conversation_history[0].timestamp
        local_timestamp = timezone.localtime(utc_timestamp)
        context['timestamp'] = local_timestamp
    else:
        context['timestamp'] = None


    return render(request, 'System/copilot.html', context)


def delete_all_conversation_history(request):
    Conversation.objects.filter(user=request.user).delete()
    return redirect('System:copilot')

