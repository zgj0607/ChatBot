import json

from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot import settings
from ckeditor_uploader import utils
from ckeditor_uploader.backends import registry
from ckeditor_uploader.utils import get_storage_class
from ckeditor_uploader.views import get_upload_filename
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.generic import View
from django.views.generic.base import TemplateView

bot = ChatBot(**settings.CHATTERBOT,
              logic_adapters=
              [
                  {
                      'import_path': 'chatbot.logic.TableLogicAdapter',
                      'default_response': 'I am sorry, but I do not understand your picture.',
                      'maximum_similarity_threshold': 0.60
                  },
                  {
                      'import_path': 'chatbot.logic.ImageLogicAdapter',
                      'default_response': 'I am sorry, but I do not understand your picture.',
                      'maximum_similarity_threshold': 0.60
                  },
                  {
                      'import_path': 'chatbot.logic.IRLogicAdapter',
                      'default_response': 'I am sorry, but I do not understand.',
                      'maximum_similarity_threshold': 0.90
                  },
                  {
                      'import_path': 'chatterbot.logic.BestMatch',
                      'default_response': 'I am sorry, but I do not understand.',
                      'maximum_similarity_threshold': 0.65
                  },
                  {
                      'import_path': 'chatterbot.logic.MathematicalEvaluation',
                  },
                  {
                      'import_path': 'chatbot.logic.TimeAdapter',
                  },
                  {
                      'import_path': 'chatterbot.logic.SpecificResponseAdapter',
                      'input_text': 'Help me!',
                      'output_text': 'Ok, here is a link: http://chatterbot.rtfd.org'
                  }
              ],
              preprocessors=[
                  'chatbot.processor.tokenizer',
              ],
              read_only=True)


class ChatterBotAppView(TemplateView):
    template_name = 'chat/chatbox.html'


class ChatterBotApiView(View):
    """
    Provide an API endpoint to interact with ChatterBot.
    """

    def post(self, request, *args, **kwargs):
        """
        Return a response to the statement in the posted data.

        * The JSON data should contain a 'text' attribute.
        """
        input_data = json.loads(request.body.decode('utf-8'))

        if 'text' not in input_data:
            return JsonResponse({
                'text': [
                    'The attribute "text" is required.'
                ]
            }, status=400)

        response = bot.get_response(input_data)

        response_data = response.serialize()

        return JsonResponse(response_data, status=200)

    def get(self, request, *args, **kwargs):
        """
        Return data corresponding to the current conversation.
        """
        return JsonResponse({
            'name': bot.name
        })


storage = get_storage_class()


class ChatterBotApiUpload(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        response = None
        if request.method == 'POST' and request.FILES:

            uploaded_file = request.FILES['file']

            backend = registry.get_backend()

            file_wrapper = backend(storage, uploaded_file)
            allow_non_images = getattr(settings, 'CKEDITOR_ALLOW_NONIMAGE_FILES', True)
            # Throws an error when an non-image file are uploaded.
            if not file_wrapper.is_image and not allow_non_images:
                response = {
                    "code": 1,
                    "msg": "我看不懂图片的意思哦，能否用语言再描述一下啊",
                    "data": {"src": ""}
                }
                return HttpResponse(json.dumps(response), content_type="application/json")

            filepath = get_upload_filename(uploaded_file.name, request)

            saved_path = file_wrapper.save_as(filepath)
            url = utils.get_media_url(saved_path)

            response = {
                "code": 0,
                "msg": url,
                "data": {"src": url}
            }

        return HttpResponse(json.dumps(response), content_type="application/json")
