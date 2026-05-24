"""
Custom Permission Classes for SIMS Backend
Role-Based Access Control (RBAC)
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission to only allow admin users."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsStaff(permissions.BasePermission):
    """Permission to only allow staff users (admin or staff)."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'staff']
        )


class IsStudent(permissions.BasePermission):
    """Permission to only allow student users."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'student'
        )


class IsParent(permissions.BasePermission):
    """Permission to only allow parent users."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'parent'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to only allow owners of an object or admins."""
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.role == 'admin':
            return True
        
        # Check if object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object is a user
        if isinstance(obj, request.user.__class__):
            return obj == request.user
        
        return False


class IsInstructorOrAdmin(permissions.BasePermission):
    """Permission for instructors to manage their courses or admin for all."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'staff']
        )
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.role == 'admin':
            return True
        
        # Check if user is the instructor of the course
        if hasattr(obj, 'instructor'):
            return obj.instructor.user == request.user
        
        if hasattr(obj, 'course') and hasattr(obj.course, 'instructor'):
            return obj.course.instructor.user == request.user
        
        if hasattr(obj, 'marked_by'):
            return obj.marked_by == request.user
        
        return False


class ReadOnly(permissions.BasePermission):
    """Permission to only allow read-only access."""
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthenticatedAndActive(permissions.BasePermission):
    """Permission to only allow authenticated and active users."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active
        )
