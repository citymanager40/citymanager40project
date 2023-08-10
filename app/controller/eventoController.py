import folium
import datetime
import geocoder
from ..database import db
from sqlalchemy import func, and_
from base64 import b64encode
from ..enum import statusEventoEnum
from flask_login import login_required, current_user
from ..models.eventoModel import Evento
from ..rotas.eventoRout import evento_bp
from ..forms.eventoForm import EventoForm
from ..models.categoriaModel import Categoria
from ..models.subcategoriaModel import Subcategoria
from app.models.eventoHistoricoModel import EventoHistorico
from app.models.eventoObservacaoModel import EventoObservacao
from flask import jsonify, render_template, request, redirect, url_for, flash, session

from .roleRequired import  roles_required

class eventoController():

    global ROWS_PER_PAGE 
    ROWS_PER_PAGE = 5

    @evento_bp.route('/home', methods=['GET'])
    @login_required
    def home():
        try:
            # Se o usário tem permissão de governo
            if 'URBANMOB_GOVERNO' in session["roles"] or 'URBANMOB_ADMIN' in session["roles"]: 
                # Lista todos os eventos cadastrados
                return redirect(url_for('evento.homeGoverno'))
            else :
                return redirect(url_for('evento.homeUsuario'))

        except Exception as e:
            flash('Erro: {}'.format(e), 'error')



    @evento_bp.route('/homeUsuario', methods=['GET'])
    @login_required
    def homeUsuario():
        # Lista apenas os eventos do usuário logado
        page = request.args.get('page', 1, type=int)

        listHistoricoEvento = EventoHistorico.query.filter(and_
        (EventoHistorico.dataFim.is_(None), EventoHistorico.evento.has(Evento.idUsuario == current_user.id))).order_by(EventoHistorico.dataInicio.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
        # (EventoHistorico.idStatusEvento != statusEventoEnum.StatusEventoEnum.FINALIZADO.value, EventoHistorico.dataFim.is_(None), EventoHistorico.evento.has(Evento.idUsuario == current_user.id))).order_by(EventoHistorico.dataInicio.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
            
        for t in listHistoricoEvento.items:
            t.evento.fileBase64 = b64encode(t.evento.file).decode()

        return render_template('home.html', listHistoricoEvento=listHistoricoEvento)


    # https://towardsdatascience.com/use-html-in-folium-maps-a-comprehensive-guide-for-data-scientists-3af10baf9190
    @evento_bp.route('/homeGoverno', methods=['GET'])
    @login_required
    @roles_required('URBANMOB_ADMIN, URBANMOB_GOVERNO')
    def homeGoverno():

        today = datetime.date.today()
        tomorrow = (today + datetime.timedelta(days=2))
        
        subquery = db.session.query(EventoHistorico.id).filter(and_(EventoHistorico.idStatusEvento == statusEventoEnum.StatusEventoEnum.FINALIZADO.value, EventoHistorico.dataInicio > tomorrow))
        listHistoricoEvento = db.session.query(EventoHistorico).filter(and_(EventoHistorico.dataFim.is_(None), ~EventoHistorico.id.in_(subquery))).all()

        contTotal = db.session.query(func.count(func.distinct(Evento.id))).scalar()
        contFinalizada = db.session.query(func.count(func.distinct(Evento.id))).filter(and_(EventoHistorico.dataFim.is_(None), EventoHistorico.idStatusEvento == statusEventoEnum.StatusEventoEnum.FINALIZADO.value)).join(EventoHistorico.evento).scalar()
        contAguardando = db.session.query(func.count(func.distinct(Evento.id))).filter(and_(EventoHistorico.dataFim.is_(None), EventoHistorico.idStatusEvento == statusEventoEnum.StatusEventoEnum.AGUARDANDO_ATENDIMENTO.value)).join(EventoHistorico.evento).scalar()

        listLat = [row.evento.txtLat for row in listHistoricoEvento]
        listLong = [row.evento.txtLong for row in listHistoricoEvento]
        listOcorrencia = ['<b>Ocorrência:</b>: ' + row.evento.numOcorrencia + '<br>' + '<b>Status:</b>: ' + row.statusEvento.txtStatusEvento + '<br>' +'<b>Problema:</b> ' + row.evento.txtProblema for row in listHistoricoEvento]
        listStatus = [row.idStatusEvento for row in listHistoricoEvento]

        map = folium.Map(location=[-9.648139, -35.717239],
                        zoom_start=10)

        for lat, lon, ocorrencia, status in zip(listLat, listLong, listOcorrencia, listStatus):
            if status == 1:
                folium.Marker(location=[float(lat), float(lon)], popup=ocorrencia, icon=folium.Icon(color="red", icon="glyphicon glyphicon-exclamation-sign")).add_to(map)
            elif status == 2 :
                folium.Marker(location=[float(lat), float(lon)], popup=ocorrencia, icon=folium.Icon(color="blue", icon="glyphicon glyphicon-exclamation-sign")).add_to(map)
            else:
                folium.Marker(location=[float(lat), float(lon)], popup=ocorrencia, icon=folium.Icon(color="green", icon="glyphicon glyphicon-exclamation-sign")).add_to(map)

        # Listagem da div da direita.
        listHistoricoEventoDireita = EventoHistorico.query.filter(and_(EventoHistorico.idStatusEvento != statusEventoEnum.StatusEventoEnum.FINALIZADO.value, EventoHistorico.dataFim.is_(None))).order_by(EventoHistorico.dataInicio.desc()).limit(10).all()
        for t in listHistoricoEventoDireita:
            t.evento.fileBase64 = b64encode(t.evento.file).decode()

        #map.save('map.html')
        mapHtml = map._repr_html_()
        return render_template('homeGoverno.html', listHistoricoEvento=listHistoricoEvento, listHistoricoEventoDireita=listHistoricoEventoDireita, mapHtml=mapHtml, contTotal=contTotal,contFinalizada=contFinalizada,contAguardando=contAguardando)

    @evento_bp.route('/listar', methods=['GET'])
    @login_required
    def listar():

        try:
            page = request.args.get('page', 1, type=int)
            
            listHistoricoEvento = EventoHistorico.query.filter(and_(EventoHistorico.idStatusEvento != statusEventoEnum.StatusEventoEnum.FINALIZADO.value, EventoHistorico.dataFim.is_(None))).order_by(EventoHistorico.dataInicio.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)    

            for t in listHistoricoEvento.items:
                t.evento.fileBase64 = b64encode(t.evento.file).decode()

        except Exception as e:
            flash('Erro: {}'.format(e), 'error')

        return render_template('listarEventos.html', listHistoricoEvento=listHistoricoEvento)

    @evento_bp.route('/evento', methods=['GET'])
    @login_required
    def iniciar():
        form = EventoForm(request.form)
        listCategoria = Categoria.query.filter(Categoria.dataFim.is_(None)).all()
        form.categoria.choices = [(0, "Selecione...")]+[(cat.id, cat.txtCategoria) for cat in listCategoria]
        return render_template('cadastrarEvento.html', listCategoria=listCategoria, form=form)

    @evento_bp.route('/cadastrar' , methods=['POST'])
    @login_required
    def cadastrar():

        form = EventoForm(request.form)

        subcategoriaSelect = form.subcategoria.data
        txtProblema = form.problema.data
        txtEndereco = form.endereco.data
        txtLat = form.latitude.data
        txtLong = form.longitude.data
        file = request.files['file']
        dataInicio = datetime.datetime.now()

        if not subcategoriaSelect:
            flash('Informe a subcategoria', 'error')
            listCategoria = Categoria.query.filter(Categoria.dataFim.is_(None)).all()
            form.categoria.choices = [(0, "Selecione...")]+[(cat.id, cat.txtCategoria) for cat in listCategoria]
            return render_template('cadastrarEvento.html', listCategoria=listCategoria, form=form)

        if not txtLat and not txtLong:
            g = geocoder.osm(txtEndereco)

            if not g:
                flash('Endereço não encontrado', 'error')
                listCategoria = Categoria.query.filter(Categoria.dataFim.is_(None)).all()
                form.categoria.choices = [(0, "Selecione...")]+[(cat.id, cat.txtCategoria) for cat in listCategoria]
                return render_template('cadastrarEvento.html', listCategoria=listCategoria, form=form)

            latlong = g.json
            txtLat = latlong['lat']
            txtLong = latlong['lng']

        numOcorrencia = str(dataInicio.year) + str(current_user.id) + str(dataInicio.day) + str(dataInicio.month) + str(dataInicio.hour) + str(dataInicio.minute) + str(dataInicio.second)

        evento = Evento(subcategoriaSelect, current_user.id, numOcorrencia, txtProblema, txtEndereco, txtLat, txtLong, file.read(), dataInicio)
        eventoHistorico= EventoHistorico(evento, statusEventoEnum.StatusEventoEnum.AGUARDANDO_ATENDIMENTO.value, current_user.id, dataInicio)

        db.session.add(eventoHistorico)
        db.session.commit()

        flash('Evento cadastrado com sucesso.', 'Sucess')

        return redirect(url_for('evento.home'))

    # https://tutorial101.blogspot.com/2021/01/python-flask-dynamic-loading-of.html
    @evento_bp.route("/loadSubcategoria",methods=["POST","GET"])
    @login_required
    def loadSubcategoria():
  
        form = EventoForm(request.form)

        if request.method == 'POST':
            category_id = request.form['id_categoria']
            listSubcategoria = Subcategoria.query.filter(Subcategoria.idCategoria == category_id).all()
            form.subcategoria.choices = [(0, "Selecione...")]+[(sub.id, sub.txtSubcategoria) for sub in listSubcategoria]
        return jsonify({'htmlresponse': render_template('subcategoriaAjax.html', listSubcategoria=listSubcategoria, form=form)})     

    @evento_bp.route('/ocorrencia/<num_ocorrencia>')
    @login_required
    def selecionarEvento(num_ocorrencia):

        eventoHistorico = db.session.query(EventoHistorico).join(Evento).filter(and_(Evento.numOcorrencia == num_ocorrencia, EventoHistorico.dataFim.is_(None))).first()
        listEventoHistorico = EventoHistorico.query.filter(EventoHistorico.idEvento==eventoHistorico.evento.id).all()

        for t in listEventoHistorico:
            t.evento.fileBase64 = b64encode(t.evento.file).decode()

        # Se o usuário tem permissão de governo
        if ('URBANMOB_GOVERNO' in session["roles"] or 'URBANMOB_ADMIN' in session["roles"]):
            return render_template('visualizarEventoGoverno.html', eventoHistorico=eventoHistorico, listEventoHistorico=listEventoHistorico)
        else: 
            return render_template('visualizarEvento.html', eventoHistorico=eventoHistorico, listEventoHistorico=listEventoHistorico)

    @evento_bp.route('/observacao/<evento_historico_id>/<num_ocorrencia>' , methods=['POST'])
    @login_required
    def cadastrarObservacao(evento_historico_id, num_ocorrencia):
        txtObservacao = request.form['observacao']
        dataInicio = datetime.datetime.now()

        try:
            eventoObservacao = EventoObservacao(evento_historico_id, current_user.id, txtObservacao, dataInicio)
            db.session.add(eventoObservacao)
            db.session.commit()

            flash('Observação cadastrada com sucesso', 'sucess')
        except Exception as e:
            db.session.rollback()
            flash('Erro: {}'.format(e), 'error')
            
        return redirect(url_for('evento.selecionarEvento', num_ocorrencia = num_ocorrencia))    

    @evento_bp.route('/atender/<num_ocorrencia>')
    @login_required
    def atender(num_ocorrencia):

        try:
            data = datetime.datetime.now()

            eventoHistorico = db.session.query(EventoHistorico).join(Evento).filter(and_(Evento.numOcorrencia == num_ocorrencia, EventoHistorico.dataFim.is_(None))).first()
            eventoHistorico.dataFim = data
            
            newEventoHistorico = EventoHistorico(eventoHistorico.evento, statusEventoEnum.StatusEventoEnum.EM_ANDAMENTO.value, current_user.id, data)
            db.session.add(newEventoHistorico)
            db.session.commit()

            flash('Evento alterado para: {status}'.format(status = statusEventoEnum.StatusEventoEnum.EM_ANDAMENTO.name), 'sucess')
        except Exception as e:
            db.session.rollback()
            flash('Erro: {}'.format(e), 'error')

        return redirect(url_for('evento.selecionarEvento', num_ocorrencia = eventoHistorico.evento.numOcorrencia))

    @evento_bp.route('/finalizar/<num_ocorrencia>')
    @login_required
    def finalizar(num_ocorrencia):

        try:
            data = datetime.datetime.now()

            eventoHistorico = db.session.query(EventoHistorico).join(Evento).filter(and_(Evento.numOcorrencia == num_ocorrencia, EventoHistorico.dataFim.is_(None))).first()

            if eventoHistorico.idStatusEvento != statusEventoEnum.StatusEventoEnum.EM_ANDAMENTO.value:
                flash('Ocorrência {} não pode ser finalizada. Atenda a ocorrência'.format(num_ocorrencia), 'error')
                return redirect(url_for('evento.selecionarEvento', num_ocorrencia = eventoHistorico.evento.numOcorrencia)) 

            eventoHistorico.dataFim = data

            newEventoHistorico= EventoHistorico(eventoHistorico.evento, statusEventoEnum.StatusEventoEnum.FINALIZADO.value, current_user.id, data)
            db.session.add(newEventoHistorico)
            db.session.commit()

            flash('Evento alterado para: {status}'.format(status = statusEventoEnum.StatusEventoEnum.FINALIZADO.name), 'sucess')
        except Exception as e:
            db.session.rollback()
            flash('Erro: {}'.format(e), 'error')

        return redirect(url_for('evento.selecionarEvento', num_ocorrencia = eventoHistorico.evento.numOcorrencia))       

    @evento_bp.route('/search', methods=["GET"])
    @login_required
    def search(): 
        numOcorrencia = request.args.get('numOcorrencia')
        eventoHistorico = EventoHistorico.query.filter(and_(EventoHistorico.dataFim.is_(None), EventoHistorico.evento.has(Evento.numOcorrencia == numOcorrencia))).first()

        if eventoHistorico == None:
             flash('Ocorrência {} não encontrada'.format(numOcorrencia), 'error')
             return redirect(url_for('evento.homeGoverno'))

        return redirect(url_for('evento.selecionarEvento', num_ocorrencia = eventoHistorico.evento.numOcorrencia))