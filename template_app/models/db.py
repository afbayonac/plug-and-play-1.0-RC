__author__ = 'Evolutiva'

# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB

    db = DAL(settings.database_uri,migrate=False, pool_size=1)

else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db = db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
response.optimize_css = 'concat,minify,inline'
response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
#from gluon.contrib.login_methods.oauth20_account import OAuthAccount
#auth.settings.login_form=OAuthAccount(
#    '451757221525971',
#    'f96ace78e220d4371ad007aafce4fd83'
#)
crud, service, plugins = Crud(db), Service(), PluginManager()

# a table for Country
db.define_table('country',
    Field('name','string', required=True),
    Field('iso2','string',required=True),
    Field('iso3','string',required=True),
    #Field('name_es','string',required=False),
    Field('iso_id','integer', required=False),
    format='%(name)s'
)
## after auth = Auth(db)
db.define_table(
    auth.settings.table_user_name,
    Field('first_name', length=128, default='',label=T('Nombre(s)')),
    Field('last_name', length=128, default='',label=T('Apellido')),
    Field('user_name', length=128, default='',label=T('Nombre de usuario'), required=True),
    Field('email', length=128, default='', unique=True), # required
    Field('password', 'password', length=512,            # required
        readable=False, label=T('Clave'),requires=IS_LENGTH(minsize=6)),
    Field('created_on','datetime',default=request.now,
        label=T('Created On'),writable=False,readable=False),
    Field('modified_on','datetime',default=request.now,
        label=T('Modified On'),writable=False,readable=False,
        update=request.now),
    Field('shortbio','text',label=T('Perfil'), required=False),
    Field('address',label=T('Dirección')),
    Field('country',db.country,label=T('País'),requires=IS_IN_DB(db, 'country.id', 'country.name'),default=44),
    Field('city',label=T('Ciudad')),
    Field('sector',label=T('Sector')),
    Field('web',label=T('Sitio Web'),required=False),
    Field('avatar','upload'),
    Field('thumbnail','upload',readable=False, writable=False),
    Field('thumbnail_mini','upload',readable=False, writable=False),
    Field('registration_key', length=512,                # required
        writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,              # required
        writable=False, readable=False, default=''),
    Field('registration_id', length=512,                 # required
        writable=False, readable=False, default=''),
    format='%(user_name)s',
    migrate=False)

## do not forget validators
custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.password.requires = CRYPT(key=auth.settings.hmac_key)
custom_auth_table.user_name.requires = IS_NOT_IN_DB(db, db.auth_user.user_name)
custom_auth_table.email.requires = (IS_EMAIL(error_message=auth.messages.invalid_email),
                               IS_NOT_IN_DB(db, db.auth_user.email))


auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table

## before auth.define_tables(username=True)

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False, migrate=False)

## configure email
mail=auth.settings.mailer
mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login

## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

auth.settings.login_url = URL('default','ingresogeneral')
auth.settings.logged_url = URL('default','editarperfil')
auth.settings.download_url = URL('default','download')
auth.settings.login_next = URL('default','index')
auth.settings.logout_next = URL('default','index')
auth.settings.profile_next = URL('default','editarperfil_ok')
auth.settings.register_next = URL('default','registrogeneral_cuentacreada')
auth.settings.retrieve_username_next = URL('default','index')
auth.settings.retrieve_password_next = URL('default','gracias')
auth.settings.change_password_next = URL('default','configuracion_ok')
auth.settings.request_reset_password_next = URL('default','gracias')
auth.settings.reset_password_next = URL('default','configuracion_ok')
#auth.messages.reset_password_next = RESET_PASSWORD_NEXT
auth.messages.reset_password = RESET_PASSWORD
auth.messages.verify_email =VERIFIY_EMAIL
#auth.messages.verify_email_subjet ="Confirmar tu registro en Poderopedia"
auth.settings.verify_email_next = URL('user', args='login')
auth.settings.register_onaccept.append(lambda form:\
mail.send(to='dev@poderopedia.com',subject='new user',
    message='new user email is %s'%form.vars.email))

##mensajes
auth.messages.submit_button = 'Enviar'
auth.messages.verify_password = 'Verificar Clave'
auth.messages.delete_label = 'Marque para borrar:'
auth.messages.function_disabled = 'Funcion dishabilitada'
auth.messages.access_denied = 'Provilegios Insuficientes'
auth.messages.registration_verifying = 'Registro necesita verificarse'
auth.messages.registration_pending = 'Registro esta pendiente de aprobación'
auth.messages.login_disabled = 'Login deshabilitado por Administrador'
auth.messages.logged_in = 'Logeado'
auth.messages.email_sent = 'Email enviado'
auth.messages.unable_to_send_email = 'Incapaz de enviar email'
auth.messages.email_verified = 'Felicidades tu Email fue verificado con Exito'
auth.messages.logged_out = 'Des-logeado'
auth.messages.registration_successful = 'Registro Exitoso'
auth.messages.invalid_email = 'El e-mail que ingresas es incorrecto o no existe en nuestro registro.'
auth.messages.unable_send_email = 'Incapaz de enviar email'
auth.messages.invalid_login = 'El correo electrónico o contraseña introducidos no coinciden con nuestros registros. Por favor ingresa los datos de nuevo.'
auth.messages.invalid_user = 'Usuario inválido'
auth.messages.is_empty = "No puede estar vacío"
auth.messages.mismatched_password = "Lo sentimos las claves no coinciden"
auth.messages.verify_email_subject = 'Confirmar tu registro en Poderopedia'
auth.messages.username_sent = 'Su nombre de usuario fue enviado por email'
auth.messages.new_password_sent = 'Su contraseña fue enviada por email'
auth.messages.password_changed = 'Contraseña cambiada'
auth.messages.retrieve_username = 'Su nombre de usuario es: %(username)s'
auth.messages.retrieve_username_subject = 'Nombre de usuario recuperado'
auth.messages.retrieve_password = 'Su contrasña es: %(password)s'
auth.messages.retrieve_password_subject = 'Contraseña recuperada'
#auth.messages.reset_password = ...
auth.messages.reset_password_subject = 'Restablecer contraseña de Poderopedia'
auth.messages.invalid_reset_password = 'Invalid reset password'
auth.messages.profile_updated = 'Actualizacion de perfil'
auth.messages.new_password = 'Contraseña nueva'
auth.messages.old_password = 'Contraseña vieja'
auth.messages.group_description =\
'Group uniquely assigned to user %(id)s'
auth.messages.register_log = 'Usuario %(id)s registrado'
auth.messages.login_log = 'Usuario %(id)s Logged-in'
auth.messages.logout_log = 'Usuario %(id)s Logged-out'
auth.messages.profile_log = 'Usuario %(id)s perfil actualizado'
auth.messages.verify_email_log = 'Usuario %(id)s Mensaje de verificación'
auth.messages.retrieve_username_log = 'Usuario %(id)s nombre de usuario recuperado'
auth.messages.retrieve_password_log = 'Usuario %(id)s contraseña recuperada'
auth.messages.reset_password_log = 'User %(id)s Password reset'
auth.messages.change_password_log = 'Usuario %(id)s Contraseña Cambiada'
auth.messages.add_group_log = 'Group %(group_id)s created'
auth.messages.del_group_log = 'Group %(group_id)s deleted'
auth.messages.add_membership_log = None
auth.messages.del_membership_log = None
auth.messages.has_membership_log = None
auth.messages.add_permission_log = None
auth.messages.del_permission_log = None
auth.messages.has_permission_log = None
auth.messages.label_first_name = 'First name'
auth.messages.label_last_name = 'Last name'
auth.messages.label_username = 'Nombre de Usuario'
auth.messages.label_email = 'E-mail'
auth.messages.label_password = 'Contraseña'
auth.messages.label_registration_key = 'Llave de registro'
auth.messages.label_reset_password_key = 'Reset Password key'
auth.messages.label_registration_id = 'Registration identifier'
auth.messages.label_role = 'Role'
auth.messages.label_description = 'Description'
auth.messages.label_user_id = 'User ID'
auth.messages.label_group_id = 'Group ID'
auth.messages.label_name = 'Name'
auth.messages.label_table_name = 'Table name'
auth.messages.label_record_id = 'Record ID'
auth.messages.label_time_stamp = 'Timestamp'
auth.messages.label_client_ip = 'Client IP'
auth.messages.label_origin = 'Origin'
auth.messages.label_remember_me = "Recuerdame (por 30 días)"

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import RPXAccount
from gluon.contrib.login_methods.extended_login_form import ExtendedLoginForm
#other_form = RPXAccount(request, api_key='594f1fcf7f1981b293d3e6a704180310da42a0e6', domain='beta.poderopedia.org', url='https://poderopedia.rpxnow.com/')
#auth.settings.login_form = ExtendedLoginForm(request,
#    auth, other_form, signals=['token'])
if request.vars._next:
    url = "http://beta.poderopedia.org/sociales/login?_next=%s" % request.vars._next
else:
    url = "http://beta.poderopedia.org/sociales/login"

rpxform = RPXAccount(request,
    api_key='594f1fcf7f1981b293d3e6a704180310da42a0e6',
    domain='poderopedia',
    url = url,
    language="es",
    embed=True
)
#auth.settings.login_form = RPXAccount(request,
#    api_key='594f1fcf7f1981b293d3e6a704180310da42a0e6',
#    domain='beta.poderopedia.org',
#    url = "https://poderopedia.rpxnow.com/")

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################




db.rdf_namespaces = {'_xmlns:rdf':"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                     '_xmlns:relational':"http://www.dbs.cs.uni-duesseldorf.de/RDF/relational.owl#"
}



def select_datewidget(field,value):
    MINYEAR = 1900
    MAXYEAR = 2040
    import datetime
    now = datetime.date.today()
    dtval = value or now.isoformat()
    year,month,day= str(dtval).split("-")
    dt = SQLFORM.widgets.string.widget(field,value)
    id = dt['_id']
    dayid = id+'__day'
    monthid = id+'__month'
    yearid = id+'__year'
    wrapperid = id+'__wrapper'
    wrapper = DIV(_id=wrapperid)
    day = SELECT([OPTION(str(i).zfill(2)) for i in range(1,32)],
        value=day,_id=dayid)
    month = SELECT([OPTION(datetime.date(2008,i,1).strftime('%B'),
        _value=str(i).zfill(2)) for i in range(1,13)],
        value=month,_id=monthid)
    year = SELECT([OPTION(i) for i in range(MINYEAR,MAXYEAR)],
        value=year,_id=yearid)
    jqscr = SCRIPT("""
      jQuery('#%s').hide();
      var curval = jQuery('#%s').val();
      if(curval) {
        var pieces = curval.split('-');
        jQuery('#%s').val(pieces[0]);
        jQuery('#%s').val(pieces[1]);
        jQuery('#%s').val(pieces[2]);
      }
      jQuery('#%s select').change(function(e) {
        jQuery('#%s').val(
           jQuery('#%s').val()+'-'+jQuery('#%s').val()+'-'+jQuery('#%s').val());
      });
    """ % (id,id,yearid,monthid,dayid,wrapperid,id,yearid,monthid,dayid))
    wrapper.components.extend([day,month,year,dt,jqscr])
    return wrapper


# a table to store mapas
db.define_table('mapas',
    Field('label', 'text', requires=IS_NOT_EMPTY(), label='Nombre?'),
    Field('posted_on', 'datetime', readable=False, writable=False),
    Field('graph', 'text', readable=False, writable=False),
    auth.signature
)



# a table to store casos
db.define_table('casos',
    Field('label', 'string', requires=IS_NOT_EMPTY(), label='Nombre'),
    Field('posted_on', 'datetime', readable=False, writable=False),
    Field('graph', 'text', readable=False, writable=False),
    auth.signature
)



# a table for place
db.define_table('place',
    Field('lugar','string',requires=True),
    Field('fecha','date',requires=IS_DATE(), required=True),
    Field('country',db.country,label='País',requires=False),
)



#a teble for sector
db.define_table('sector',
    Field('parent','integer',required=True, default=0),
    Field('name','string', required=True),
    Field('labelOtro', 'string', readable=False, writable=False),
    format='%(name)s'
)

##from plugin_anytime_widget import anytime_widget, anydate_widget, anydatetime_widget



# a table document
db.define_table('document',
    Field('name','string', label=T('Descripción')),
    Field('documentURL','string',requires=IS_URL(), label=T('URL'), required=True),
    Field('fecha','string', label=T('Fecha Documento')),
    Field('tipoDoc', 'string', required=False, readable=False, writable=False),
    Field('source_from',db.auth_user, readable=True, writable=False, required=True, default=auth.user_id),
    auth.signature,
    format='%(name)s'
)
requiere=db((db.document.source_from==auth.user_id)&(db.document.is_active==True))

##tabla caso
db.define_table('caso',
    Field('depiction', 'upload', label=T('Logotipo')),
    Field('name','string',label=T('Nombre')),
    Field('description','text',label=T('Reseña')),
    Field('country',db.country,label=T('País'),requires=IS_IN_DB(db, 'country.id', 'country.name'),default=44),
    Field('city','string',label=T('Ciudad')),
    Field('documentSource','list:reference document',required=False,
        requires=IS_IN_DB(requiere,'document.id','%(name)s / (documentURL)s',multiple=True),
        label=T('Fuentes')),
    Field('documentCloud','list:reference documentCloud',required=False,
          requires=IS_IN_DB(db,'documentCloud.id','%(title)s',multiple=True),
          label=T('Fuentes Document Cloud')),
    auth.signature,
    format='%(name)s'
)

# a table to store personas
db.define_table('persona',
    Field('ICN','string',label=T('rut'), required=False),
    Field('firstName', 'string', readable=True, writable=True, label=T('Nombres')),
    Field('firstLastName', 'string', requires=IS_NOT_EMPTY(), label=T('Apellido 1')),
    Field('otherLastName', 'string', readable=True, writable=True, label=T('Apellido 2')),
    Field('alias', 'string', requires=IS_NOT_EMPTY(), readable=True, writable=True, label=T('Nombre Corto')),
    ##Field('birth', db.birthEvent, label='Fecha de Nacimiento', required=False),
    Field('birth', 'string', label='Fecha de Nacimiento', required=False),
    Field('countryofResidence',db.country, label='País de Residencia'),
    Field('Mainsector','list:reference sector', label=T('Sector Principal')),
    ##Field('depiction',db.document, label=T('Foto')),
    Field('depiction','upload', label=T('Foto'), required=False),
    Field('shortBio','text', label=T('Reseña')),
    Field('longBio','text', label=T('Perfil largo')),
    Field('documentSource','list:reference document',required=False,
        requires=IS_IN_DB(requiere,'document.id','%(name)s / %(documentURL)s',multiple=True),
        label=T('Fuentes')),
    Field('documentCloud','list:reference documentCloud',required=False,
        requires=IS_IN_DB(db,'documentCloud.id','%(title)s',multiple=True),
        label=T('Fuentes Document Cloud')),
    ##Field('hasAlternativeMainSector','string',readable=False, writable=False, label=T('Sector Principal Alternativo')),
    ##Field('hasAlternativeOtherSector','string',readable=False, writable=False, label=T('Otro Sector Alternativo')),
    Field('isDead','boolean', label=T('Ha Fallecido')),
    Field('web','string', label=T('Web')),
    Field('twitterNick','string', label=T('Twitter')),
    Field('facebookNick','string', label=T('Facebook')),
    Field('linkedinNick','string', label=T('Linkedin')),
    ##Field('hasdocumentation',db.document, label=T('Documento')),
    ##Field('hasdocumentation','upload', label=T('Documento')),
    ##Field('hasUrl',db.document, label=T('Redes Sociales')),
    auth.signature,
    format='%(alias)s')




db.define_table('persona_archive',
    Field('current_record','integer'),
    db.persona,
    format='%(alias)s')



db.persona.firstName.rdf= 'foaf:firstName'
db.persona.firstLastName.rdf= 'poder:firstLastName'
db.persona.otherLastName.rdf= 'poder:otherLastName'
db.persona.alias.rdf= 'poder:alias'

db.persona.rdf={
    'type': 'foaf:Person',
    '_rdf:about':'poder:alias',
    '_rdf:label':'poder:alias',
    'namespaces': {
        '_xmlns:foaf':'http://xmlns.com/foaf/0.1/',
        '_xmlns:poder':'http://poderopedia.com/vocab/'
    }
}

db.country.rdf={
    'type':'poder:Country',
    '_rdf:about':'name',
    '_rdf:label':'name',
    'namespaces': {
        '_xmlns:geo':'http://www.w3.org/2003/01/geo/wgs84_pos/',
        '_xmlns:poder':'http://poderopedia.com/vocab/'
    }
}

##relacion caso a persona
db.define_table('relCasoPersona',
    Field('origenP',db.persona),
    Field('destinoC',db.caso,widget = SQLFORM.widgets.autocomplete(request, db.caso.name,
        id_field=db.caso.id, keyword='_autocomplete_destinoC_%(fieldname)s', db=db(db.caso.is_active==True))),
    Field('fdesde','string', required=False, label=T('Desde')),
    Field('fhasta', 'string', required=False, label=T('Hasta')),
    Field('isPast','boolean', required=False, label=T('es pasado')),
    Field('context','string',required=True, label=T('Razon del Vínculo')),
    Field('documentSource','list:reference document',required=False,
        requires=IS_IN_DB(requiere,'document.id','%(name)s',multiple=True),
        label=T('Fuentes')),
    auth.signature
)


# a table to store perfiles
db.define_table('perfiles',
    Field('label', 'string', requires=IS_NOT_EMPTY(), label='Nombre?'),
    Field('postedon', 'datetime', readable=False, writable=False),
    Field('dueno', 'reference auth_user', readable=False, writable=False),
    Field('graph', 'text', readable=False, writable=False),
    Field('person','reference persona', readable=False, writable=False)
)

#a table for sectorMain2Pers
db.define_table('sectorMain2Pers',
    Field('origenP',db.persona),
    Field('destinoSector',db.sector)
)

# table for tipoParentesco
db.define_table('tipoParentesco',
    Field('name','string', required=True, label=T('Parentesco')),
    Field('nameInverso','string', required=False),
    Field('description','text', required=False),
    format='%(name)s'
)



#table for tipoRelacionP2P
db.define_table('tipoRelacionP2P',
    Field('parent','integer',required=True, default=0),
    Field('name','string', required=True),
    Field('description','text', required=False),
    format='%(name)s'
)


#table for tipoOrganizacion
db.define_table('tipoOrganizacion',
    Field('name','string', required=True),
    Field('generalizacion','integer'),
    #Field('keyword','string'),
    format='%(name)s'
)

db.define_table('Organizacion',
    Field('name','string', required=False, label=T('Nombre'), writable=False, readable=False),
    Field('tipoOrg',db.tipoOrganizacion, label=T('Tipo Organizacion'), default=12),
    Field('haslogo','upload',uploadfield=True, label=T('Logo')),
    Field('hasSocialReason','string', label=T('Razón Social')),
    Field('Mainsector','list:reference sector', label=T('Sector Principal')),
    Field('hasTaxId','string',label=T('RUT')),
    Field('alias','string', label=T('Nombre Fantasía')),
    Field('countryOfResidence',db.country, label=T('Casa Matriz')),
    Field('depiction','upload', label='Foto'),
    Field('hasdocumentation','upload', label='Documento'),
    Field('documentSource','list:reference document',required=False,
        requires=IS_IN_DB(requiere,'document.id','%(name)s / %(documentURL)s',multiple=True),
        label=T('Fuentes')),
    Field('documentCloud','list:reference documentCloud',required=False,
        requires=IS_IN_DB(db,'documentCloud.id','%(title)s',multiple=True),
        label=T('Fuentes Document Cloud')),
    Field('shortBio','text', label='Reseña'),
    Field('longBio','text', label='Perfil largo'),
    Field('birth', 'string', label='Fecha de Fundación'),
    auth.signature,
    format='%(alias)s'
)

db.define_table('Organizacion_archive',
    Field('current_record','integer'),
    db.Organizacion,
    format='%(alias)s'
)

#table for RelPersona
db.define_table('relPersona',
    Field('relacion',db.tipoRelacionP2P, required=True, requires=IS_IN_DB(db, 'tipoRelacionP2P.id', 'tipoRelacionP2P.name')),
    Field('origenP',db.persona, requires=IS_IN_DB(db, 'persona.id', 'persona.alias')),
    Field('destinoP',db.persona, widget = SQLFORM.widgets.autocomplete(request, db.persona.alias,
        id_field=db.persona.id, keyword='_autocomplete_destinoP_%(fieldname)s', db=db(db.persona.is_active==True))),
    Field('extraO', db.Organizacion, widget = SQLFORM.widgets.autocomplete(
        request, db.Organizacion.alias, id_field=db.Organizacion.id, db=db(db.Organizacion.is_active==True)),
        requires=False, label=T('Organizacion/Empresa')),
    Field('extraLabel','string',required=False, label=T('Sub Grupo')),
    Field('fdesde','string', required=False, label=T('Desde')),
    Field('fhasta', 'string', required=False, label=T('Hasta')),
    Field('isPast','boolean', required=False, label=T('es pasado')),
    Field('documentSource','list:reference document',required=False,
        requires=IS_IN_DB(requiere,'document.id','%(name)s / (documentURL)s',multiple=True),
        label=T('Fuentes')),
    Field('ini','date',readable=False,writable=False),
    Field('fin','date',readable=False,writable=False),
    auth.signature,
)

#table type of relation Org2Org
db.define_table('tipoRelacionOrg2Org',
    Field('parent','integer',label='Padre', required=True, default=0),
    Field('name','string',label='Nombre', required=True),
    Field('inverse','string'),
    format='%(name)s'
)

#table relation Organization to Organization
db.define_table('relOrg2Org',
    Field('origenO',db.Organizacion,label='Origen',required=True, requires=IS_IN_DB(db,'Organizacion.id','db.Organizacion.alias')),
    Field('relationOrg',db.tipoRelacionOrg2Org,required=True),
    Field('destinoO',db.Organizacion,label='Destino',required=True),
    Field('extraLabel','string', required=False, label=T('Sub Grupo')),
    Field('fdesde','string', required=False, notnull=False, label=T('Desde')),
    Field('fhasta','string', required=False, notnull=False, label=T('Hasta')),
    Field('isPast','boolean', label='es pasado'),
    Field('documentSource','list:reference document',required=False,
        requires=IS_IN_DB(requiere,'document.id','%(name)s / (documentURL)s',multiple=True),
        label=T('Fuentes')),
    Field('ini','date',readable=False,writable=False),
    Field('fin','date',readable=False,writable=False),
    auth.signature
)

db.relOrg2Org.destinoO.widget = SQLFORM.widgets.autocomplete(
    request, db.Organizacion.alias, id_field=db.Organizacion.id, db=db(db.Organizacion.is_active==True))
db.relOrg2Org.documentSource.widget=SQLFORM.widgets.multiple.widget

#table tipoRelacionP20
db.define_table('tipoRelacionP20',
    Field('parent','integer',required=True, default=0),
    Field('relationship','string', required=True),
    Field('generalizacion','string'),
    Field('inverse','string'),
    Field('orden','integer'),
    format='%(relationship)s'
)

#table RelPersOrg
db.define_table('RelPersOrg',
    Field('specificRelation',db.tipoRelacionP20,required=True,requires=IS_IN_DB(db, 'tipoRelacionP20.id', 'tipoRelacionP20.relationship'),label='Conexion'),
    Field('origenP',db.persona,required=True, requires=IS_IN_DB(db, 'persona.id', 'persona.alias')),
    Field('destinoO',db.Organizacion),
    Field('fdesde','string', required=False, notnull=False, label=T('Desde')),
    Field('fhasta','string', required=False, notnull=False, label=T('Hasta')),
    Field('isPast','boolean', label='es pasado'),
    Field('extraLabel','string', required=False, label=T('Sub Grupo')),
    Field('documentSource','list:reference document',required=False,
        requires=IS_IN_DB(requiere,'document.id','%(name)s / (documentURL)s',multiple=True),
        label=T('Fuentes')),
    Field('transitive','integer',required=False,readable=False,writable=False),
    Field('transitiveP2P','integer',required=False,readable=False,writable=False),
    Field('ini','date',readable=False,writable=False),
    Field('fin','date',readable=False,writable=False),
    auth.signature
)

db.RelPersOrg.destinoO.widget = SQLFORM.widgets.autocomplete(
    request, db.Organizacion.alias, id_field=db.Organizacion.id)
db.RelPersOrg.documentSource.widget=SQLFORM.widgets.multiple.widget




#table for relFamiliar
db.define_table('relFamiliar',
    Field('parentesco',db.tipoParentesco, required=True, requires=IS_IN_DB(db, 'tipoParentesco.id', 'tipoParentesco.name'), label='Relacion'),
    Field('origenP',db.persona, required=True, requires=IS_IN_DB(db(db.persona.is_active==True), 'persona.id', 'persona.alias'), label='Persona'),
    Field('destinoP',db.persona,
        widget=SQLFORM.widgets.autocomplete(request, db.persona.alias, id_field=db.persona.id,keyword='_autocomplete_destinoP_%(fieldname)s',db=db(db.persona.is_active==True))),
    Field('documentSource','list:reference document',required=False,
        requires=IS_IN_DB(requiere,'document.id','%(name)s / (documentURL)s',multiple=True),
        label=T('Fuentes')),
    auth.signature
)
# a table birthEvent
db.define_table('birthEvent',
    Field('hasSource',db.document,label=T('Fuente'),requires=False),
    Field('place',db.place, requires=False),
    Field('fecha','date',requires=IS_DATE(), required=True),
    auth.signature,
    format='%(fecha)s'
)



db.define_table('companeros',
    Field('relacionP2O',db.RelPersOrg,label=T('Estudios'),required=True, readable=False, writable=False),
    Field('nexo','string',label=T('Nexo'), required=False),
    Field('relationComp','integer',required=True, readable=False,writable=False),
    Field('destinoP', db.persona, label=T('Persona'), required=True,
        widget=SQLFORM.widgets.autocomplete(request, db.persona.alias,
            id_field=db.persona.id, keyword='_autocomplete_destinoP_%(fieldname)s',db=db(db.persona.is_active==True))),
    Field('fechaI','string',required=False, label=T('Fecha Inicio')),
    Field('fechaF','string',required=False, label=T('Fecha Final')),
    Field('fuente','list:reference document',label=T('Fuente'), requires=IS_IN_DB(requiere,'document.id','%(name)s/%(documentURL)s',
        multiple=True)),
    auth.signature
)



db.define_table('importer',
    Field('filename', 'upload', autodelete=True),
    auth.signature
)

##notificaciones

##TODO considerar archivo
##sugerir_conexion
entityList=['persona','empresa','organizacion']
estadoList=['sin revision','rechazada','aprobada / en curso / asignado']
db.define_table('sugerirConexion',
    Field('referenceEntity', 'string',requires=IS_IN_SET(entityList),label=T('Seleccione Entidad'),writable=False,readable=True),
    Field('reference', 'integer', writable=False,readable=True,required=True, requires=IS_NOT_EMPTY(error_message=T('complete este campo!'))),
    Field('alias', 'string', writable=False,readable=True,required=True, requires=IS_NOT_EMPTY(T('complete este campo!'))),
    Field('name','string',required=True,label=T('Quiero sugerir'), requires=IS_NOT_EMPTY(T('complete este campo!'))),
    Field('texto','text',label=T('¿Cómo están relacionados?'), required=True, requires=IS_NOT_EMPTY(T('complete este campo!'))),
    Field('documentURL','string',requires=IS_URL(T('ingrese URL válida!')), label=T('Obtuve esta información de'), required=True, default='Ingresa =URL'),
    Field('estado','string',requires=IS_IN_SET(estadoList), default='sin revision',writable=False,readable=True),
    auth.signature
)

##sugerir persona
db.define_table('sugerirPersona',
    Field('name','string',required=True,label=T('Quiero sugerir el perfil de'),requires=IS_NOT_EMPTY(error_message=T('complete este campo!'))),
    Field('texto','text',label=T('¿Por qué es importante?'),requires=IS_NOT_EMPTY(error_message=T('complete este campo!'))),
    Field('documentURL','string',requires=IS_URL(T('ingrese URL válida!')), label=T('Obtuve esta información de'), required=True),
    Field('estado','string',requires=IS_IN_SET(estadoList), default='sin revision',writable=False,readable=True),
    auth.signature
)




##TODO
##enviar amigo

##TODO
##seguerir perfil
#db.define_table('sugerirPerfil',
#    Field('nombre','string',required=True,label=T('Quiero sugerir el perfil de')),
#    Field('contenido','text',label=T('¿Por qué es importante?')),
#    Field('URL','string',requires=IS_URL(), label=T('Obtuve esta información de'), required=True),
#    Field('estado','list:string',requires=IS_IN_SET(estadoList), default='sin revision'),
#    auth.signature
#)

##TODO
##invita a colaborar

##TODO
##notificaciones
errorEstado=['reportarError','contenidoInadecuado']
db.define_table('notificaciones',
    Field('referenceEntity','string',requires=IS_IN_SET(entityList),label=T('Conexión con'),writable=False,readable=True),
    Field('reference', 'integer', writable=False,readable=True),
    Field('contenido','text',label=T('¿Cual es el contenido inadecuado?')),
    Field('URL','string',requires=IS_URL(), label=T('Obtuve esta información de'), required=True),
    Field('tipoError',requires=IS_IN_SET(errorEstado),writable=False,readable=True),
    Field('estado','string',requires=IS_IN_SET(estadoList), default='sin revision',writable=False,readable=True),
    auth.signature
)

##notificaciones tipoerror
#errorEstado=['reportarError','contenidoInadecuado']

db.define_table('tipoerror',
    Field('referenceEntity','string',requires=IS_IN_SET(entityList),label=T('Reportar Error en:'),writable=False,readable=True),
    Field('reference', 'integer', writable=False,readable=True),
    Field('contenido','text',label=T('¿Cual es el Error?'),requires=IS_NOT_EMPTY(T('complete este campo!'))),
    Field('URL','string',requires=IS_URL(T('Ingrése una URL válida!')), label=T('Obtuve esta información de'), required=True),
    #Field('tipoError',requires=IS_IN_SET(errorEstado),writable=False,readable=True),
    Field('estado','string',requires=IS_IN_SET(estadoList), default='sin revision',writable=False,readable=True),
    auth.signature
)

##notificaciones tipoerror
#errorEstado=['reportarError','contenidoInadecuado']
db.define_table('tipoinadecuado',
    Field('referenceEntity','string',requires=IS_IN_SET(entityList),label=T('Reportar Contenido Inadecuado en:'),writable=False,readable=True),
    Field('reference', 'integer', writable=False,readable=True),
    Field('contenido','text',label=T('¿Cual es el Contenido Inadecuado?'),requires=IS_NOT_EMPTY(T('complete este campo!'))),
    Field('URL','string',requires=IS_URL(T('Ingrése una URL válida!')), label=T('Obtuve esta información de'), required=True),
    #Field('tipoError',requires=IS_IN_SET(errorEstado),writable=False,readable=True),
    Field('estado','string',requires=IS_IN_SET(estadoList), default='sin revision',writable=False,readable=True),
    auth.signature
    )

##compartir a un amigo
db.define_table('compartir',
    Field('email','string',required=True,label=T('Email'),requires=IS_EMAIL()),
    Field('contenido','text',label=T('mensaje')),
    Field('fecha','date',writable=False,readable=False,default=request.now),
    Field('pagina','string',writable=False,readable=False),
    )


##TODO
##tengo un dato
db.define_table('tengoDato',
    Field('nombre','string',required=True,label=T('Tengo datos importantes sobre'),requires=IS_NOT_EMPTY(T('complete este campo!'))),
    Field('contenido','text',label=T('Si tienes información exclusiva sobre una Persona, Empresa, Organización o Caso que ya incluimos en Poderopedia o aún no está agregado aquí.Respetamos tu anonimato.Sientete libre de escribirnos a datos@poderopedia.org'),requires=IS_NOT_EMPTY(T('complete este campo!'))),
    Field('URL','string',requires=IS_URL(T('ingrese URL válida!')), label=T('Obtuve esta información de'), required=True),
    Field('estado','string',requires=IS_IN_SET(estadoList), default='sin revision',writable=False,readable=True),
    Field('created_on','datetime',default=request.now)
)
me= auth.user_id
accessList=['public','private','organization']
db.define_table('documentCloud',
    Field('dc_id','string'),
    Field('file', 'upload'),
    Field('title', 'string', required=True,requires=IS_ALPHANUMERIC(), label=T('Titulo Documento')),
    Field('source', 'string', label=T('Fuente del Documento')),
    Field('description', 'text',label=T('Descripción del Documento')),
    Field('related_article', 'string',label=T('URL'),comment=T('the URL of the article associated with the document')),
    Field('published_url', 'string',label=T('URL'),comment=T('the URL of the page on which the document will be embedded')),
        Field('access', 'list:string', requires=IS_IN_SET(accessList)),
    Field('project', 'integer'),
    Field('data', 'string',default='{"date":'+str(request.now)+', "auth_user":'+str(me)+'}'),
    Field('secure', 'string',default='false'),
    auth.signature
)
