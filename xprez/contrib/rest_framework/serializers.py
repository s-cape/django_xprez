from rest_framework import serializers

from xprez.models import Module


class ModuleSerializer(serializers.ModelSerializer):
    html = serializers.SerializerMethodField()

    def get_html(self, obj):
        return obj.polymorph().render_front(self.context)

    class Meta:
        model = Module
        fields = ("position", "html")
