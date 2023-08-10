from flask_login import login_required
from flask import render_template, flash, request, jsonify
from app.enum.statusEventoEnum import StatusEventoEnum
from app.models.categoriaModel import Categoria
from app.models.statusEventoModel import StatusEvento
from app.models.subcategoriaModel import Subcategoria
from app.models.userModel import User
from app.models.eventoHistoricoModel import EventoHistorico
from app.models.eventoModel import Evento
from ..rotas.eventoSearchRout import evento_search_bp
from sqlalchemy import func, and_
from ..database import db

class eventoSearchController:

    global ROWS_PER_PAGE 
    ROWS_PER_PAGE = 5

    @evento_search_bp.route('/prepareSearch', methods=['GET'])
    @login_required
    def prepareSearch():

        global listCategoria 
        global listStatus
        global listUsuario
        global numOcorrenciaSearch
        global statusSearch
        global categoriaSearch
        global dataFimSearch
        global userSearch

        listCategoria = Categoria.query.filter(Categoria.dataFim.is_(None)).all()
        listStatus = StatusEvento.query.filter(StatusEvento.dataFim.is_(None)).all()
        listUsuario = User.query.all()
        listEventoHistoricoSearch = None
        numOcorrenciaSearch = None
        statusSearch = None
        categoriaSearch = None
        dataFimSearch = None
        userSearch = None

        return render_template('filtraEventos.html', listCategoria=listCategoria, listStatus=listStatus, listUsuario=listUsuario, listEventoHistoricoSearch=listEventoHistoricoSearch, numOcorrenciaSearch=numOcorrenciaSearch, statusSearch=statusSearch, categoriaSearch=categoriaSearch, dataFimSearch=dataFimSearch, userSearch=userSearch)


    @evento_search_bp.route('/eventoSearch', methods=['GET'])
    @login_required
    def search():

        try:

            numOcorrenciaSearch = request.args.get('numOcorrenciaSearch')
            statusSearch = request.args.get('statusSearch') 
            categoriaSearch = request.args.get('categoriaSearch') 
            dataInicioSearch = request.args.get('dataInicioSearch') 
            dataFimSearch = request.args.get('dataFimSearch') 
            userSearch = request.args.get('userSearch')

            if numOcorrenciaSearch == "" and statusSearch == "" and categoriaSearch == "" and dataInicioSearch == "" and dataFimSearch == "" and userSearch == "":
                listEventoHistoricoSearch = None
                flash('Informe pelo menos um critério de pesquisa', 'error')
                return render_template('filtraEventos.html', listCategoria=listCategoria, listStatus=listStatus, listUsuario=listUsuario, listEventoHistoricoSearch=listEventoHistoricoSearch)

            page = request.args.get('page', 1, type=int)
       
            querySearch = EventoHistorico.query.filter(EventoHistorico.dataFim.is_(None))

            if numOcorrenciaSearch != "":
                querySearch= querySearch.join(EventoHistorico.evento).filter(Evento.numOcorrencia == numOcorrenciaSearch)

            if statusSearch != "":
                querySearch= querySearch.join(EventoHistorico.statusEvento).filter(StatusEvento.id == statusSearch)

            if categoriaSearch != "":
                querySearch = querySearch.join(EventoHistorico.evento).join(Evento.subcategoria).join(Subcategoria.categoria).filter(Categoria.id == categoriaSearch)

            if userSearch != "":
                querySearch = querySearch.join(EventoHistorico.evento).join(Evento.usuario).filter(User.name.ilike('%' + str(userSearch) + '%'))

            if dataInicioSearch != "" and dataFimSearch != "":
                querySearch = querySearch.join(EventoHistorico.evento).filter(Evento.dataInicio >= dataInicioSearch).filter(Evento.dataInicio <= dataFimSearch)
            elif dataInicioSearch != "" and dataFimSearch == "":
                querySearch = querySearch.join(EventoHistorico.evento).filter(Evento.dataInicio >= dataInicioSearch)
            elif dataInicioSearch == "" and dataFimSearch != "":
                querySearch = querySearch.join(EventoHistorico.evento).filter(Evento.dataInicio <= dataFimSearch)

            listEventoHistoricoSearch = querySearch.order_by(EventoHistorico.dataInicio.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)

            if listEventoHistoricoSearch.items == []:
                listEventoHistoricoSearch = None
                flash('A pesquisa não encontrou nenhum resultado', 'error')
                return render_template('filtraEventos.html', listCategoria=listCategoria, listStatus=listStatus, listUsuario=listUsuario, listEventoHistoricoSearch=listEventoHistoricoSearch)

        except Exception as e:
            flash('Erro: {}'.format(e), 'error')

        return render_template('filtraEventos.html', listCategoria=listCategoria, listStatus=listStatus, listUsuario=listUsuario, listEventoHistoricoSearch=listEventoHistoricoSearch, numOcorrenciaSearch=numOcorrenciaSearch,  statusSearch=statusSearch, categoriaSearch=categoriaSearch, dataFimSearch=dataFimSearch, userSearch=userSearch)


    @evento_search_bp.route('/userAutocomplete', methods=['GET'])
    def userAutocomplete():
        userSearch = request.args.get('userSearch')
        listUsuarioAutocomplete = User.query.filter(User.name.ilike('%' + str(userSearch) + '%')).all()
        results = [user.name for user in listUsuarioAutocomplete]
        return jsonify(results=results) 

    @evento_search_bp.route('/estatisticas', methods=['GET'])
    @login_required
    def estatisticas():

        contTotal = db.session.query(func.count(func.distinct(Evento.id))).scalar()
        contFinalizada = db.session.query(func.count(func.distinct(Evento.id))).filter(and_(EventoHistorico.dataFim.is_(None), EventoHistorico.idStatusEvento == StatusEventoEnum.FINALIZADO.value)).join(EventoHistorico.evento).scalar()
        contAndamento = db.session.query(func.count(func.distinct(Evento.id))).filter(and_(EventoHistorico.dataFim.is_(None), EventoHistorico.idStatusEvento == StatusEventoEnum.EM_ANDAMENTO.value)).join(EventoHistorico.evento).scalar()
        contAguardando = db.session.query(func.count(func.distinct(Evento.id))).filter(and_(EventoHistorico.dataFim.is_(None), EventoHistorico.idStatusEvento == StatusEventoEnum.AGUARDANDO_ATENDIMENTO.value)).join(EventoHistorico.evento).scalar()
        
        perTotal = (contTotal / contTotal ) * 100
        perFinalizada = (contFinalizada / contTotal ) * 100
        perAndamento = (contAndamento / contTotal ) * 100
        perAguardando = (contAguardando / contTotal ) * 100

        print('xxxxxx', contFinalizada);

        return render_template('estatisticas.html', contTotal=contTotal, contFinalizada=contFinalizada, contAndamento=contAndamento, contAguardando=contAguardando,
        perTotal=round(perTotal,3), perFinalizada=round(perFinalizada,2), perAndamento=round(perAndamento,2), perAguardando=round(perAguardando,2))    