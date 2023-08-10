from ..database import db

class StatusEvento(db.Model):
    __tablename__ = 'tb_status_evento_sev'
    __table_args__ = {"schema":"mob"}
    
    id = db.Column('id_status_evento_sev', db.Integer, autoincrement=True, primary_key=True)
    txtStatusEvento = db.Column('txt_status_evento_sev', db.String(50), nullable=False)
    dataInicio = db.Column('dat_inicio_sev', db.DateTime, nullable=False)
    dataFim = db.Column('dat_fim_sev', db.DateTime, nullable=True)

    def __init__(self, txtStatusEvento, dataInicio):
        self.txtStatusEvento = txtStatusEvento
        self.dataInicio = dataInicio