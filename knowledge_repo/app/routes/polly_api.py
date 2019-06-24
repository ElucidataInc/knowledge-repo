"""
APIs for polly and their routes
Includes:
    - /api/uploadkr
    - /api/uploadpost
    - /api/uploadpage

"""

import os
import json
from builtins import str
from collections import namedtuple
from flask import request, render_template, redirect, Blueprint, current_app, make_response,jsonify,url_for, Response
from flask_login import login_required
from sqlalchemy import case, desc
from sqlalchemy.exc import IntegrityError
from werkzeug import secure_filename
from .. import permissions
from ..proxies import db_session, current_repo
from ..utils.posts import get_posts
from ..models import Post, Tag, User, PageView
from ..utils.requests import from_url_get_feed_params
from ..utils.render import render_post_tldr
from ..utils.s3_talk import download_dir,download_from_s3, create_kr
from ..index import update_index, update_index_for_post
blueprint = Blueprint('api', __name__, template_folder='../templates', static_folder='../static')




def publish_post_db(kp,path):
    if not kp.is_valid():
        print("KP was invalid")
        return

    print("Checking the DB for this:",path)
    post = (db_session.query(Post).filter(Post.path==path).first())
    if not post:
        print(u'creating new post from path {}'.format(kp.path))
        post = Post()
        db_session.add(post)
        db_session.commit()
        db_session.flush()  # (matthew) Fix groups logic so this is not necessary
    try:
        post.update_metadata_from_kp(kp)
        print("After update:", post.path)
    except IntegrityError:
        import uuid
        db_session.rollback()
        print("from the caller:",kp.path)
        kp.uuid = str(uuid.uuid4())
        post.update_metadata_from_kp(kp)
        print("After update:", post.path)
    db_session.commit()
    db_session.flush()

        # Record revision
#    for uri, revision in current_repo.revisions.items():
#        IndexMetadata.set('repository_revision', uri, str(revision))

def prep_kr_path(path,dir_name):
    path_parts = path.split('/')
    if '/'.join(path_parts[:2]) != dir_name:
        path = dir_name + '/' + path
    if not path.endswith('.kp'):
        path = path + '.kp'
    return path

def prep_post_path(path):
    if not path.endswith('.kp'):
        path = path + '.kp'
    return path


@blueprint.route('/api/uploadpage')
@PageView.logged
def upload_post_page(): 
    try:
        kr_list = current_app.get_kr_list()
    except ValueError:
        return redirect("https://%s/?next=%s"%(request.host,request.full_path))
    return render_template('upload_page.html',krs = kr_list)

@blueprint.route('/api/uploadpost',methods=['POST'])
def upload_post():
    # Access the file
    #TODO: Put everything in try catch
    tempfile = request.files['file']
    temp_path = os.path.join('/tmp',secure_filename(tempfile.filename))
    tempfile.save(temp_path)
    repo = request.form.get('repo')
    path = repo + '/' + request.form.get('path')
    # Just post the post to the path
    try:
        new_post = current_repo.upload_post(temp_path,path)
    #    update_index_for_post(new_post,path)
        path = prep_post_path(path)
        publish_post_db(new_post,path)
    except:
        return render_template("error.html")
    return redirect(url_for('posts.render',path=path))

@blueprint.route('/api/uploadkr')
@PageView.logged
def upload_kr():
    """
    API to upload a KR to the server
    args:
        S3-Path 
    """
    import shutil
    global current_repo,current_app
    from ...repositories.meta import MetaKnowledgeRepository
    path = request.args.get('path')
    pid = path.split('/')[-2]
    dir_name,dir_path = download_dir(path)
    dir_name = pid + '/' + dir_name
    error = 200
    #try:
    db_path = current_app.config['KR_REPO_DB_PATH'] + ':' +  dir_name
    dbobj  = current_repo.migrate_to_dbrepo(dir_path,db_path)
    current_app.append_repo_obj(dir_name,dbobj)
    temp_kr = MetaKnowledgeRepository({dir_name:dbobj})
    for post in temp_kr.posts():
        post_path = prep_kr_path(post.path,dir_name)
        print("Tried pushing:",post_path)
        publish_post_db(post,post_path)
    #except:
   #TODO: do more precise exception handling
    #    error = 400
    shutil.rmtree(dir_path)
    return jsonify({
                'statusCode': '400' if error==400 else '200',
                'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                            },
                   })

@blueprint.route('/api/addkr')
@PageView.logged
def add_kr():
    """
    API to add a KR both to the server, database and s3 bucket
    args:
        Project id
        Kr name
    """
    resp = Response(status = 501, mimetype='application/json')

    # handling edge error conditions
    if 'pid' not in request.args:
      data = {'error' : 'pid is not in arguments'}
      resp.status_code = 400
      resp.data = json.dumps(data)
      return resp
    
    if 'kr' not in request.args:
      data = {'error' : 'kr is not in arguments'}
      resp.status_code = 400
      resp.data = json.dumps(data)
      return resp

    pid = request.args.get('pid')
    kr_name = request.args.get('kr')

    if len(pid) == 0:
      data = {'error' : 'Pid can not be empty'}
      resp.status_code = 400
      resp.data = json.dumps(data)
    
    if len(kr_name) == 0:
      data = {'error' : 'Kr name can not be empty'}
      resp.status_code = 400
      resp.data = json.dumps(data)

    dir_name = pid + '/' + kr_name

    # adding kr to s3 bucket
    ret_val = create_kr(kr_name, pid)
    if ret_val == -1:
      resp.status_code = 409
      data = {'error': 'Kr name already exists'}
      resp.data = json.dumps(data)
      return resp

    # adding kr to server and database

    db_path = current_app.config['KR_REPO_DB_PATH'] + ':' +  dir_name
    dbobj = current_repo.create_dbrepo(db_path)
    current_app.append_repo_obj(dir_name,dbobj)

    data = {'error': 'Kr has been created'}
    resp.data = json.dumps(data)
    resp.status_code = 201
    return resp


