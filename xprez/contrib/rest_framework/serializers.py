from rest_framework import serializers

from xprez.models import Content


class ContentSerializer(serializers.ModelSerializer):
    html = serializers.SerializerMethodField()

    def get_html(self, obj):
        return obj.polymorph().render_front()

    class Meta:
        model = Content
        fields = ('position', 'html')


