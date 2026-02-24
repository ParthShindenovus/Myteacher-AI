from rest_framework import serializers


class NormalizeInputSerializer(serializers.Serializer):
    inputType = serializers.ChoiceField(choices=["text", "voice", "image"])
    text = serializers.CharField(required=False, allow_blank=True)
    audioUrl = serializers.CharField(required=False, allow_blank=True)
    imageUrl = serializers.CharField(required=False, allow_blank=True)


class DecomposeRequestSerializer(serializers.Serializer):
    sessionId = serializers.CharField()
    normalizedQuery = serializers.DictField()
