from ..database import db

class Categoria(db.Model):
    __tablename__ = 'tb_categoria_cat'
    __table_args__ = {"schema":"mob"}
    
    id = db.Column('id_categoria_cat', db.Integer, autoincrement=True, primary_key=True)
    txtCategoria = db.Column('txt_categoria_cat', db.String(50), nullable=False)
    dataInicio = db.Column('dat_inicio_cat', db.DateTime, nullable=False)
    dataFim = db.Column('dat_fim_cat', db.DateTime, nullable=True)

    def __init__(self, txtCategoria, dataInicio, dataFim):
        self.txtCategoria = txtCategoria
        self.dataInicio = dataInicio
        self.dataFim = dataFim