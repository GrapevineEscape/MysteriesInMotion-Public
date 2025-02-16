import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.performer.forms import PerformerProfileForm
from app.models import User, Show, Role, RoleApplication, ShowDate, Rehearsal
from app.extensions import db
from app.admin.routes import get_event_color
from flask import jsonify


performer_bp = Blueprint('performer', __name__)

UPLOAD_FOLDER = 'app/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@performer_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('performer/dashboard.html')

@performer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = PerformerProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.address = form.address.data
        current_user.phone = form.phone.data
        current_user.bio = form.bio.data

        # Handle file upload
        if form.headshot.data:
            headshot_file = form.headshot.data
            filename = f"{current_user.id}_headshot.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            headshot_file.save(filepath)
            current_user.headshot_path = f"/static/uploads/{filename}"

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('performer.profile'))

    return render_template('performer/profile.html', form=form)



@performer_bp.route('/shows')
@login_required
def view_shows():
    shows = Show.query.all()
    return render_template('performer/view_shows.html', shows=shows)


@performer_bp.route('/shows/<int:show_id>/roles')
@login_required
def view_roles(show_id):
    show = Show.query.get_or_404(show_id)
    roles = Role.query.filter_by(show_id=show.id).all()

    # Get application status for the current user
    applications = {app.role_id: app.status for app in RoleApplication.query.filter_by(performer_id=current_user.id).all()}

    return render_template('performer/view_roles.html', show=show, roles=roles, applications=applications)


@performer_bp.route('/apply/<int:role_id>', methods=['POST'])
@login_required
def apply_for_role(role_id):
    role = Role.query.get_or_404(role_id)
    existing_application = RoleApplication.query.filter_by(
        performer_id=current_user.id, role_id=role.id
    ).first()

    if existing_application:
        flash('You have already applied for this role.', 'info')
        return redirect(url_for('performer.view_roles', show_id=role.show_id))

    new_application = RoleApplication(
        performer_id=current_user.id,
        show_id=role.show_id,
        role_id=role.id
    )
    db.session.add(new_application)
    db.session.commit()
    flash(f'Application for the role "{role.name}" submitted successfully!', 'success')
    return redirect(url_for('performer.view_roles', show_id=role.show_id))


# CALENDAR
@performer_bp.route('/calendar')
@login_required
def performer_calendar():
    """Display Performer Calendar with non-DRAFT Show Dates and Rehearsals."""
    events = []
    
    # Fetch scheduled shows that are NOT in Draft mode
    scheduled_shows = ShowDate.query.filter(ShowDate.status != 'Draft').order_by(ShowDate.date).all()

    for show_date in scheduled_shows:
        # Primary show date event
        events.append({
            'id': show_date.id,
            'title': f"{show_date.show.title} ({show_date.status})",
            'start': show_date.date.isoformat(),
            'color': get_event_color(show_date.status),
            'extendedProps': {
                'show': show_date.show.title,
                'location': show_date.location,
                'status': show_date.status,
                'rehearsals': [
                    {
                        'date': r.date.strftime('%Y-%m-%d %H:%M'),
                        'location': r.location
                    }
                    for r in show_date.rehearsals
                ]
            }
        })

        # Add individual rehearsal events
        for rehearsal in show_date.rehearsals:
            events.append({
                'id': f"rehearsal-{rehearsal.id}",
                'title': f"Rehearsal: {show_date.show.title}",
                'start': rehearsal.date.isoformat(),
                'color': 'lightblue',
                'extendedProps': {
                    'location': rehearsal.location,
                    'show': show_date.show.title,
                    'type': 'Rehearsal'
                }
            })

    return render_template('performer/calendar.html', events=events, scheduled_shows=scheduled_shows)


# VIEW EVENTS
@performer_bp.route('/calendar/event/<int:show_date_id>')
@login_required
def get_performer_event_details(show_date_id):
    """Fetch show date and rehearsals for Performers when they click an event."""
    show_date = ShowDate.query.get_or_404(show_date_id)

    event_details = {
        'title': show_date.show.title,
        'date': show_date.date.strftime('%Y-%m-%d %H:%M'),
        'location': show_date.location,
        'status': show_date.status,
        'rehearsals': [
            {
                'date': rehearsal.date.strftime('%Y-%m-%d %H:%M'),
                'location': rehearsal.location
            } for rehearsal in show_date.rehearsals
        ]
    }

    return jsonify(event_details)


# REHEARSAL EVENTS
@performer_bp.route('/calendar/rehearsal/<int:rehearsal_id>')
@login_required
def get_rehearsal_details(rehearsal_id):
    """Fetch rehearsal details for a clicked calendar entry."""
    rehearsal = Rehearsal.query.get_or_404(rehearsal_id)

    rehearsal_data = {
        'title': f"Rehearsal for {rehearsal.show_date.show.title}",
        'date': rehearsal.date.strftime('%Y-%m-%d %H:%M'),
        'location': rehearsal.location,
        'status': "Rehearsal",
        'rehearsals': []  # Rehearsals don’t have sub-rehearsals, so this is empty
    }

    return jsonify(rehearsal_data)



