from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

from .models import Note
from .serializers import NoteSerializer


class NoteListCreateAPIView(APIView):
    """
    Handles:
    - GET  /api/notes/        -> List all notes for logged-in user
    - POST /api/notes/        -> Create a new note
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all notes for the logged-in user"""
        notes = Note.objects.filter(user=request.user).order_by('-created_at')
        serializer = NoteSerializer(notes, many=True)
        return Response(
            {
                "message": "Your notes",
                "count": notes.count(),
                "notes": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """Create a new note for the logged-in user"""
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            note = serializer.save(user=request.user)

            # EMAIL ON NOTE CREATE
            try:
                send_mail(
                    subject="Note Created",
                    message=f"Your note '{note.title}' was created successfully.",
                    from_email=None,
                    recipient_list=[request.user.email],
                )
            except Exception as e:
                print(f"Email error: {e}")

            return Response(
                {
                    "message": "Note created successfully",
                    "note": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class NoteDetailAPIView(APIView):
    """
    Handles:
    - GET    /api/notes/<id>/ -> Retrieve a single note
    - PUT    /api/notes/<id>/ -> Update a note
    - DELETE /api/notes/<id>/ -> Delete a note
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """
        Ensures that the note belongs to the logged-in user.
        Returns 404 if note not found or belongs to another user.
        """
        return get_object_or_404(Note, pk=pk, user=user)

    def get(self, request, pk):
        """Get a specific note (only if it belongs to the user)"""
        note = self.get_object(pk, request.user)
        serializer = NoteSerializer(note)
        return Response(
            {
                "message": "Note retrieved successfully",
                "note": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        """Update a specific note (only if it belongs to the user)"""
        note = self.get_object(pk, request.user)
        serializer = NoteSerializer(note, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Note updated successfully",
                    "note": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        """Delete a specific note (only if it belongs to the user)"""
        note = self.get_object(pk, request.user)
        note.delete()

        return Response(
            {"message": "Note deleted successfully"},
            status=status.HTTP_200_OK
        )

