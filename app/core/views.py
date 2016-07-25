# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import redirect, render_template, render_template_string, Blueprint
from flask import request, url_for
from flask_user import current_user, login_required, roles_accepted
from app import app, db
from app.core.models import UserProfileForm, Plugin, Upvote

core_blueprint = Blueprint('core', __name__, url_prefix='/')


# The Home page is accessible to anyone
@core_blueprint.route('')
def home_page():
    sub_query = db.session.query(Upvote.plugin_id, db.func.count('*').\
        label('upvote_count')).\
        group_by(Upvote.plugin_id).subquery()

    has_liked_query = db.session.query(Upvote, db.func.exists(Upvote.user_id == current_user.id).\
            label('has_upvoted')).subquery()

    plugins = db.session.query(Plugin, sub_query.c.upvote_count).\
        outerjoin(sub_query, Plugin.id==sub_query.c.plugin_id).order_by(Plugin.id)
        # outerjoin(has_liked_query, current_user.id==has_liked_query.c.user_id).order_by(Plugin.id)

    return render_template('core/home_page.html', plugins=plugins)

@core_blueprint.route('my-plugins', methods=['GET', 'POST'])
def plugin_form():
    if request.method == 'POST':
        form = request.form
        plugin = Plugin(name=form['name'],
                        description=form['description'],
                        user_id=current_user.id,
                        repo_url=form['repo_url'],
                        image_url=form['image_url'])
        plugin.upvotes = [
            Upvote(user_id=current_user.id, plugin_id=plugin.id)
        ]
        db.session.add(plugin)
        db.session.commit()

    plugins = Plugin.query.filter_by(user_id=current_user.id)
    return render_template('core/plugin_manager.html', plugins=plugins)

# The User page is accessible to authenticated users (users that have logged in)
@core_blueprint.route('user')
@login_required  # Limits access to authenticated users
def user_page():
    return render_template('core/user_page.html')


# The Admin page is accessible to users with the 'admin' role
@core_blueprint.route('admin')
@roles_accepted('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('core/admin_page.html')


@core_blueprint.route('user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('core.home_page'))

    # Process GET or invalid POST
    return render_template('core/user_profile_page.html',
                           form=form)


# Register blueprint
app.register_blueprint(core_blueprint)
