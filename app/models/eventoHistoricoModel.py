from ..database import db
from . import statusEventoModel, eventoModel


class EventoHistorico(db.Model):
    __tablename__ = 'tb_evento_historico_ehi'
    __table_args__ = {"schema":"mob"}
    
    id = db.Column('id_evento_historico_ehi', db.Integer, autoincrement=True, primary_key=True)
    idEvento = db.Column('id_evento_ehi',db.Integer, db.ForeignKey('mob.tb_evento_eve.id_evento_eve'), nullable=False)
    idStatusEvento = db.Column('id_status_evento_ehi', db.Integer, db.ForeignKey('mob.tb_status_evento_sev.id_status_evento_sev'), nullable=False)
    idUsuario = db.Column('id_usuario_ehi', db.Integer, db.ForeignKey('comum.tb_usuario_usu.id_usuario_usu'), nullable=False)
    dataInicio = db.Column('dat_inicio_ehi', db.DateTime, nullable=False)
    dataFim = db.Column('dat_fim_ehi', db.DateTime, nullable=True)

    evento = db.relationship("Evento") 
    statusEvento = db.relationship("StatusEvento")
    usuario = db.relationship("User")
    listObservacao = db.relationship("EventoObservacao", back_populates="eventoHistorico")

    def __init__(self, evento, idStatusEvento, idUsuario, dataInicio):
        self.evento = evento
        self.idStatusEvento = idStatusEvento
        self.idUsuario = idUsuario
        self.dataInicio = dataInicio