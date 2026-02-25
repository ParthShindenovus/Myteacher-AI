from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_tutor.agents.workflow import build_tutoring_graph
from ai_tutor.decomposer.graph import build_decomposer_graph
from ai_tutor.decomposer.repository import StateRepository
from ai_tutor.input_layer.normalizer import normalize_input
from ai_tutor.serializers import (
    DecomposeRequestSerializer,
    NormalizeInputSerializer,
    TutoringWorkflowSerializer,
)
from ai_tutor.services.logging import configure_logging, get_logger

configure_logging()
logger = get_logger("ai_tutor")


class NormalizeInputAPIView(APIView):
    @extend_schema(request=NormalizeInputSerializer)
    def post(self, request):
        serializer = NormalizeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        normalized = normalize_input(payload["inputType"], payload)
        logger.info("normalized_input", input_type=payload["inputType"], subject=normalized.subject)
        return Response(normalized.model_dump(), status=status.HTTP_200_OK)


class DecomposeQuestionAPIView(APIView):
    @extend_schema(request=DecomposeRequestSerializer)
    def post(self, request):
        serializer = DecomposeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["sessionId"]
        normalized_query = serializer.validated_data["normalizedQuery"]

        graph = build_decomposer_graph()
        result = graph.invoke({"normalized_query": normalized_query, "decomposed": {}})
        decomposed = result["decomposed"]

        try:
            StateRepository().save(session_id, decomposed)
        except Exception as exc:
            logger.warning("redis_store_failed", session_id=session_id, error=str(exc))

        logger.info("question_decomposed", session_id=session_id, subgoals=len(decomposed.get("subgoals", [])))
        return Response(decomposed, status=status.HTTP_200_OK)


class TutoringWorkflowAPIView(APIView):
    @extend_schema(request=TutoringWorkflowSerializer)
    def post(self, request):
        serializer = TutoringWorkflowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        graph = build_tutoring_graph()
        result = graph.invoke(
            {
                "input": payload,
                "normalized_query": {},
                "decomposed": {},
                "status_trail": [],
            }
        )

        response_payload = {
            "normalizedQuery": result["normalized_query"],
            "decomposed": result["decomposed"],
            "statusTrail": result["status_trail"],
        }
        logger.info(
            "workflow_completed",
            session_id=payload.get("sessionId", "default-session"),
            statuses=len(result["status_trail"]),
        )
        return Response(response_payload, status=status.HTTP_200_OK)
