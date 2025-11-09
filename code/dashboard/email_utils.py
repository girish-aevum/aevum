"""
Email utility functions for Dashboard notifications
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_early_access_confirmation_email(early_access_request):
    """
    Send confirmation email to user who submitted early access request
    """
    try:
        subject = "Thank you for your interest in Aevum Health!"
        
        # Email context
        context = {
            'user_name': early_access_request.full_name,
            'interest': early_access_request.get_interest_display_name(),
            'request_id': str(early_access_request.request_id),
            'support_email': settings.CONTACT_EMAIL,
        }
        
        # Render HTML email
        html_content = render_to_string('emails/early_access_confirmation.html', context)
        text_content = render_to_string('emails/early_access_confirmation.txt', context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[early_access_request.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Early access confirmation email sent to {early_access_request.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send early access confirmation email: {e}")
        return False


def send_early_access_admin_notification(early_access_request):
    """
    Send notification email to admin about new early access request
    """
    try:
        subject = f"New Early Access Request - {early_access_request.full_name}"
        
        # Email context
        context = {
            'request': early_access_request,
            'admin_url': f"{settings.SITE_URL}admin/dashboard/earlyaccessrequest/{early_access_request.id}/change/",
        }
        
        # Render HTML email
        html_content = render_to_string('emails/early_access_admin_notification.html', context)
        text_content = render_to_string('emails/early_access_admin_notification.txt', context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Early access admin notification sent for {early_access_request.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send early access admin notification: {e}")
        return False


def send_contact_message_confirmation_email(contact_message):
    """
    Send confirmation email to user who submitted contact message
    """
    try:
        subject = "We received your message - Aevum Health"
        
        # Email context
        context = {
            'user_name': contact_message.full_name,
            'subject': contact_message.subject,
            'message_id': str(contact_message.message_id),
            'support_email': settings.CONTACT_EMAIL,
        }
        
        # Render HTML email
        html_content = render_to_string('emails/contact_message_confirmation.html', context)
        text_content = render_to_string('emails/contact_message_confirmation.txt', context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[contact_message.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Contact message confirmation email sent to {contact_message.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send contact message confirmation email: {e}")
        return False


def send_contact_message_admin_notification(contact_message):
    """
    Send notification email to admin about new contact message
    """
    try:
        subject = f"New Contact Message - {contact_message.subject}"
        
        # Email context
        context = {
            'message': contact_message,
            'admin_url': f"{settings.SITE_URL}admin/dashboard/contactmessage/{contact_message.id}/change/",
        }
        
        # Render HTML email
        html_content = render_to_string('emails/contact_message_admin_notification.html', context)
        text_content = render_to_string('emails/contact_message_admin_notification.txt', context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Contact message admin notification sent for {contact_message.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send contact message admin notification: {e}")
        return False


def send_dashboard_emails(instance, email_type):
    """
    Convenience function to send both user and admin emails
    
    Args:
        instance: EarlyAccessRequest or ContactMessage instance
        email_type: 'early_access' or 'contact_message'
    
    Returns:
        dict: Status of both email sends
    """
    results = {
        'user_email_sent': False,
        'admin_email_sent': False,
        'errors': []
    }
    
    try:
        if email_type == 'early_access':
            results['user_email_sent'] = send_early_access_confirmation_email(instance)
            results['admin_email_sent'] = send_early_access_admin_notification(instance)
        elif email_type == 'contact_message':
            results['user_email_sent'] = send_contact_message_confirmation_email(instance)
            results['admin_email_sent'] = send_contact_message_admin_notification(instance)
        else:
            results['errors'].append(f"Unknown email type: {email_type}")
            
    except Exception as e:
        results['errors'].append(str(e))
        logger.error(f"Error in send_dashboard_emails: {e}")
    
    return results 


def send_dna_kit_order_user_notification(order):
    """
    Send confirmation email to user about DNA kit order
    """
    try:
        subject = f"Your Aevum DNA Kit Order Confirmation - {order.order_id}"
        
        # Email context
        context = {
            'user_name': order.user.first_name or order.user.username,
            'order_id': str(order.order_id),
            'kit_type': order.kit_type.name,
            'order_date': order.order_date,
            'total_amount': order.total_amount,
            'status': order.status,
            'support_email': settings.CONTACT_EMAIL,
        }
        
        # Render HTML email
        html_content = render_to_string('emails/dna_kit_order_user_confirmation.html', context)
        text_content = render_to_string('emails/dna_kit_order_user_confirmation.txt', context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"DNA kit order confirmation email sent to {order.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send DNA kit order confirmation email: {e}")
        return False


def send_dna_kit_order_admin_notification(order):
    """
    Send notification email to admin about new DNA kit order
    """
    try:
        subject = f"New DNA Kit Order - {order.order_id}"
        
        # Email context
        context = {
            'order': order,
            'user_details': order.user,
            'admin_url': f"{settings.SITE_URL}admin/dna_profile/dnakitorder/{order.id}/change/",
        }
        
        # Render HTML email
        html_content = render_to_string('emails/dna_kit_order_admin_notification.html', context)
        text_content = render_to_string('emails/dna_kit_order_admin_notification.txt', context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"DNA kit order admin notification sent for order {order.order_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send DNA kit order admin notification: {e}")
        return False 


def send_dna_results_ready_notification(order, dna_report):
    """
    Send notification email to user when DNA results are ready
    """
    try:
        # Validate inputs
        if not order:
            logger.error("No order provided for DNA results notification")
            return False
        
        if not order.user:
            logger.error(f"No user associated with order {order.order_id}")
            return False
        
        if not order.user.email:
            logger.error(f"No email found for user of order {order.order_id}")
            return False
        
        if not dna_report:
            logger.error(f"No DNA report for order {order.order_id}")
            return False

        # Prepare email subject
        subject = f"Your DNA Results are Ready - Order {order.order_id}"
        
        # Prepare key findings for email
        key_findings = dna_report.key_findings or []
        top_findings = key_findings[:3]  # Limit to top 3 findings
        
        # Prepare findings summary
        findings_summary = []
        for finding in top_findings:
            trait = finding.get('trait', 'Unknown Trait')
            value = finding.get('value', 'N/A')
            confidence = finding.get('confidence', 'Unknown')
            findings_summary.append(f"{trait}: {value} (Confidence: {confidence})")
        
        # Email context
        context = {
            'user_name': order.user.first_name or order.user.username,
            'order_id': str(order.order_id),
            'kit_type': order.kit_type.name if hasattr(order, 'kit_type') else 'DNA Kit',
            'report_id': str(dna_report.report_id),
            'generated_date': dna_report.generated_date,
            'results_count': len(key_findings),
            'top_findings': findings_summary,
            'report_url': dna_report.report_file_url or '#',
            'support_email': settings.CONTACT_EMAIL,
            'recommendations': dna_report.recommendations or 'No specific recommendations available.'
        }
        
        # Render HTML email
        html_content = render_to_string('emails/dna_results_ready_notification.html', context)
        text_content = render_to_string('emails/dna_results_ready_notification.txt', context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"DNA results ready notification sent to {order.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send DNA results ready notification: {e}", exc_info=True)
        return False 