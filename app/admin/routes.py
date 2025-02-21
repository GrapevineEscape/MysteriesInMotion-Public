import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import RoleApplication, User, Show, Role, ShowDate, Rehearsal
from app.extensions import db
from app.admin.forms import ShowForm, RoleForm
from app.admin import admin_bp 
import logging
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

UPLOAD_FOLDER = 'app/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Ensure logs directory exists
log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
os.makedirs(log_dir, exist_ok=True)


# Setup logging
admin_logger = logging.getLogger('admin')
handler = logging.FileHandler('logs/admin.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
admin_logger.addHandler(handler)
admin_logger.setLevel(logging.INFO)


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('performer.dashboard'))
    return render_template('admin/dashboard.html')



@admin_bp.route('/shows', methods=['GET', 'POST'])
@login_required
def manage_shows():
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('performer.dashboard'))

    shows = Show.query.all()
    form = ShowForm()

    if form.validate_on_submit():
        # Handle file uploads
        script_file = form.script.data
        image_file = form.image.data

        script_path = None
        if script_file:
            script_filename = f"{form.title.data}_script.pdf"
            script_path = os.path.join(UPLOAD_FOLDER, script_filename)
            script_file.save(script_path)

        image_path = None
        if image_file:
            image_filename = f"{form.title.data}_image.png"
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            image_file.save(image_path)

        new_show = Show(
            title=form.title.data,
            description=form.description.data,
            type=form.type.data,
            kid_friendly=form.kid_friendly.data,
            script_path=script_path,
            image_path=image_path
        )
        db.session.add(new_show)
        db.session.commit()
        flash("Show added successfully!", "success")
        return redirect(url_for('admin.manage_shows'))

    return render_template('admin/manage_shows.html', form=form, shows=shows)


@admin_bp.route('/shows/delete/<int:show_id>', methods=['POST'])
@login_required
def delete_show(show_id):
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('performer.dashboard'))

    show = Show.query.get_or_404(show_id)
    db.session.delete(show)
    db.session.commit()
    flash("Show deleted successfully.", "info")
    return redirect(url_for('admin.manage_shows'))



@admin_bp.route('/shows/<int:show_id>/roles', methods=['GET', 'POST'])
@login_required
def manage_roles(show_id):
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('performer.dashboard'))

    show = Show.query.get_or_404(show_id)
    form = RoleForm()

    if form.validate_on_submit():
        new_role = Role(
            name=form.name.data,
            gender=form.gender.data,
            age=form.age.data,
            description=form.description.data,
            show_id=show.id
        )
        db.session.add(new_role)
        db.session.commit()
        flash("Role added successfully!", "success")
        return redirect(url_for('admin.manage_roles', show_id=show.id))

    roles = Role.query.filter_by(show_id=show.id).all()
    return render_template('admin/manage_roles.html', form=form, show=show, roles=roles)



@admin_bp.route('/shows/<int:show_id>/roles/delete/<int:role_id>', methods=['POST'])
@login_required
def delete_role(show_id, role_id):
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('performer.dashboard'))

    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    flash("Role deleted successfully!", "info")
    return redirect(url_for('admin.manage_roles', show_id=show_id))



@admin_bp.route('/shows/<int:show_id>/roles/edit/<int:role_id>', methods=['GET', 'POST'])
@login_required
def edit_role(show_id, role_id):
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('performer.dashboard'))

    role = Role.query.get_or_404(role_id)
    form = RoleForm(obj=role)

    if form.validate_on_submit():
        role.name = form.name.data
        role.gender = form.gender.data
        role.age = form.age.data
        role.description = form.description.data
        db.session.commit()
        flash("Role updated successfully!", "success")
        return redirect(url_for('admin.manage_roles', show_id=show_id))

    return render_template('admin/edit_role.html', form=form, show_id=show_id)



@admin_bp.route('/applications')
@login_required
def view_applications():
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('performer.dashboard'))

    # Filter applications based on query parameters
    status = request.args.get('status')
    show_id = request.args.get('show_id')

    query = RoleApplication.query

    if status:
        query = query.filter_by(status=status)
    if show_id:
        query = query.filter_by(show_id=show_id)

    applications = query.all()

    shows = Show.query.all()
    return render_template('admin/view_applications.html', applications=applications, shows=shows)



@admin_bp.route('/applications/<int:app_id>/approve', methods=['POST'])
@login_required
def approve_application(app_id):
    application = RoleApplication.query.get_or_404(app_id)
    application.status = 'Approved'
    db.session.commit()
    admin_logger.info(f"Approved application for role '{application.role.name}' by performer '{application.performer.email}'")
    flash(f"Application for role '{application.role.name}' approved.", "success")
    return redirect(url_for('admin.view_applications'))



@admin_bp.route('/applications/<int:app_id>/reject', methods=['POST'])
@login_required
def reject_application(app_id):
    application = RoleApplication.query.get_or_404(app_id)
    application.status = 'Rejected'
    db.session.commit()
    admin_logger.info(f"Rejected application for role '{application.role.name}' by performer '{application.performer.email}'")
    flash(f"Application for role '{application.role.name}' rejected.", "danger")
    return redirect(url_for('admin.view_applications'))



@admin_bp.route('/applications/bulk_action', methods=['POST'])
@login_required
def bulk_application_action():
    action = request.form.get('action')
    application_ids = request.form.getlist('application_ids')

    if not application_ids:
        flash("No applications selected.", "warning")
        return redirect(url_for('admin.view_applications'))

    applications = RoleApplication.query.filter(RoleApplication.id.in_(application_ids)).all()

    for application in applications:
        if action == 'approve':
            application.status = 'Approved'
            admin_logger.info(f"Bulk approved application for role '{application.role.name}' by performer '{application.performer.email}'")
        elif action == 'reject':
            application.status = 'Rejected'
            admin_logger.info(f"Bulk rejected application for role '{application.role.name}' by performer '{application.performer.email}'")

    db.session.commit()
    flash(f"{len(applications)} application(s) have been {action}d.", "success")
    return redirect(url_for('admin.view_applications'))



@admin_bp.route('/calendar/<int:show_date_id>')
@login_required
def show_subcalendar(show_date_id):
    """Show the sub-calendar for rehearsals for a particular show date."""
    show_date = ShowDate.query.get_or_404(show_date_id)
    rehearsals = show_date.rehearsals

    events = []
    for rehearsal in rehearsals:
        events.append({
            'title': 'Rehearsal',
            'start': rehearsal.date.isoformat(),
            'color': 'lightblue',
            'notes': rehearsal.notes
        })

    return render_template('admin/subcalendar.html', show_date=show_date, events=events)


def get_event_color(status):
    """Return color based on event status."""
    colors = {
        'Draft': 'gray',
        'Open': 'green',
        'Fully Cast': 'purple',
        'Closed': 'white',
        'Canceled': 'red'
    }
    return colors.get(status, 'blue')


@admin_bp.route('/calendar')
@login_required
def calendar_view():
    """Display Admin Calendar with Show Dates, Scheduled Shows, and Rehearsals."""
    events = []
    scheduled_shows = ShowDate.query.order_by(ShowDate.date).all()

    for show_date in scheduled_shows:
        # Primary show date event
        events.append({
            'id': show_date.id,
            'title': f"{show_date.show.title} ({show_date.status})",
            'start': show_date.date.isoformat(),
            'color': get_event_color(show_date.status),
            'url': url_for('admin.edit_show_date', show_date_id=show_date.id),
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

        # Add individual rehearsal events for visibility on the calendar
        for rehearsal in show_date.rehearsals:
            events.append({
                'id': f"rehearsal-{rehearsal.id}",  # ✅ Add a unique ID for rehearsals
                'title': f"Rehearsal: {show_date.show.title}",
                'start': rehearsal.date.isoformat(),
                'color': 'lightblue',
                'extendedProps': {
                    'location': rehearsal.location,
                    'show': show_date.show.title,
                    'type': 'Rehearsal',
                    'rehearsal_id': rehearsal.id  # ✅ Explicitly include the rehearsal ID
                }
            })

    return render_template('admin/calendar.html', events=events, scheduled_shows=scheduled_shows)


def get_event_color(status):
    """Return color based on show status."""
    colors = {
        'Draft': 'gray',
        'Open': 'green',
        'Canceled': 'red',
        'Closed': 'white'
    }
    return colors.get(status, 'blue')




# Create New Show Date
@admin_bp.route('/calendar/new', methods=['GET', 'POST'])
@login_required
def create_show_date():
    if request.method == 'POST':
        # Capture main show details
        show_id = request.form.get('show_id')
        date_str = request.form.get('date')
        location = request.form.get('location')
        status = 'Draft'

        # Validate date and location
        if not date_str or not location:
            flash('Show date and location are required!', 'danger')
            return redirect(url_for('admin.calendar_view'))

        # Convert date string to datetime object
        try:
            show_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash('Invalid date format. Please use the datetime picker.', 'danger')
            return redirect(url_for('admin.calendar_view'))

        # Create and save the main show date
        new_show = ShowDate(show_id=show_id, date=show_date, location=location, status=status)
        db.session.add(new_show)
        db.session.commit()

        # Handle rehearsal dates
        rehearsal_dates = request.form.getlist('rehearsal_date[]')
        rehearsal_locations = request.form.getlist('rehearsal_location[]')

        for r_date, r_loc in zip(rehearsal_dates, rehearsal_locations):
            if r_date and r_loc:
                try:
                    rehearsal_date = datetime.strptime(r_date, "%Y-%m-%dT%H:%M")
                    rehearsal = Rehearsal(show_date_id=new_show.id, date=rehearsal_date, location=r_loc)
                    db.session.add(rehearsal)
                except ValueError:
                    flash(f"Invalid rehearsal date '{r_date}' skipped.", 'warning')

        db.session.commit()

        flash("New Show Date with rehearsals created in Draft mode!", "success")
        return redirect(url_for('admin.calendar_view'))

    # Fetch shows for dropdown
    shows = Show.query.all()
    return render_template('admin/new_show_date.html', shows=shows)


# Edit Show Date & Change Status
@admin_bp.route('/show_date/edit/<int:show_date_id>', methods=['GET', 'POST'])
@login_required
def edit_show_date(show_date_id):
    show_date = ShowDate.query.get_or_404(show_date_id)

    if request.method == 'POST':
        show_date.date = datetime.strptime(request.form.get('date'), "%Y-%m-%dT%H:%M")
        show_date.location = request.form.get('location')
        show_date.status = request.form.get('status')

        # Retrieve rehearsal data
        rehearsal_ids = request.form.getlist('rehearsal_id[]')
        rehearsal_dates = request.form.getlist('rehearsal_date[]')
        rehearsal_locations = request.form.getlist('rehearsal_location[]')
        delete_rehearsal_ids = request.form.getlist('delete_rehearsal_id[]')

        print("Rehearsal Data Received:", rehearsal_ids, rehearsal_dates, rehearsal_locations)  # Debugging Output
        print("Rehearsals to Delete:", delete_rehearsal_ids)  # Debugging Output

        # Delete flagged rehearsals
        for rehearsal_id in delete_rehearsal_ids:
            rehearsal_to_delete = Rehearsal.query.get(int(rehearsal_id))
            if rehearsal_to_delete:
                db.session.delete(rehearsal_to_delete)

        # Process rehearsals
        for i in range(len(rehearsal_dates)):
            if rehearsal_dates[i] and rehearsal_locations[i]:  # Ensure fields are not empty
                rehearsal_date = datetime.strptime(rehearsal_dates[i], "%Y-%m-%dT%H:%M")
                rehearsal_location = rehearsal_locations[i]

                if rehearsal_ids[i] == "new":
                    # Create new rehearsal
                    new_rehearsal = Rehearsal(show_date_id=show_date.id, date=rehearsal_date, location=rehearsal_location)
                    db.session.add(new_rehearsal)
                else:
                    # Update existing rehearsal
                    existing_rehearsal = Rehearsal.query.get(int(rehearsal_ids[i]))
                    if existing_rehearsal:
                        existing_rehearsal.date = rehearsal_date
                        existing_rehearsal.location = rehearsal_location

        db.session.commit()
        flash("Show date updated successfully!", "success")
        return redirect(url_for('admin.calendar_view'))

    return render_template('admin/edit_show_date.html', show_date=show_date)



# DELETE Show Date
@admin_bp.route('/show_date/delete/<int:show_date_id>', methods=['POST'])
@login_required
def delete_show_date(show_date_id):
    """Delete a show date with AJAX and confirmation."""
    
    print("Received request to delete show:", show_date_id)
    print("Request Headers:", request.headers)
    print("Request Data:", request.get_data(as_text=True))

    data = request.get_json()
    confirmation = data.get('confirmation')

    if confirmation != 'DELETE':
        return jsonify({'error': 'Invalid confirmation. Type DELETE to confirm.'}), 400

    show_date = ShowDate.query.get(show_date_id)
    if not show_date:
        return jsonify({'error': 'Show date not found.'}), 404

    db.session.delete(show_date)
    db.session.commit()
    return jsonify({'message': f'Show date "{show_date.id}" deleted successfully.'}), 200


# GET Calendar Details
@admin_bp.route('/calendar/event/<int:show_date_id>')
@login_required
def get_event_details(show_date_id):
    """Fetch show date and rehearsals for the clicked calendar event."""
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




@admin_bp.route('/calendar/rehearsal/<int:rehearsal_id>')
@login_required
def get_rehearsal_details(rehearsal_id):
    """Fetch rehearsal details separately from show events."""
    rehearsal = Rehearsal.query.get_or_404(rehearsal_id)

    rehearsal_details = {
        'title': f"Rehearsal for {rehearsal.show_date.show.title}",
        'date': rehearsal.date.strftime('%Y-%m-%d %H:%M'),
        'location': rehearsal.location,
        'status': "Rehearsal"
    }
    return jsonify(rehearsal_details)


@admin_bp.route('/performers')
def performer_list():
    performers = Performer.query.order_by(Performer.last_name, Performer.first_name).all()
    return render_template('admin/performer_list.html', performers=performers)

@admin_bp.route('/performers/<int:performer_id>')
def performer_detail(performer_id):
    performer = Performer.query.get_or_404(performer_id)
    return render_template('admin/performer_detail.html', performer=performer)


