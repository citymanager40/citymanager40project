from ..database import db

class Subcategoria(db.Model):
    __tablename__ = 'tb_subcategoria_sub'
    __table_args__ = {"schema":"mob"}
    
    id = db.Column('id_subcategoria_sub', db.Integer, autoincrement=True, primary_key=True)
    txtSubcategoria = db.Column('txt_subcategoria_sub', db.String(50), nullable=False)
    dataInicio = db.Column('dat_inicio_sub', db.DateTime, nullable=False)
    dataFim = db.Column('dat_fim_sub', db.DateTime, nullable=True)

    idCategoria = db.Column('id_categoria_sub',db.Integer, db.ForeignKey('mob.tb_categoria_cat.id_categoria_cat'), nullable=False)
    categoria = db.relationship("Categoria")