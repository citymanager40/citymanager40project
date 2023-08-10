from ..database import db

class Evento(db.Model):
    __tablename__ = 'tb_evento_eve'
    __table_args__ = {"schema":"mob"}
    
    id = db.Column('id_evento_eve', db.Integer, autoincrement=True, primary_key=True)
    idSubcategoria = db.Column('id_subcategoria_eve',db.Integer, db.ForeignKey('mob.tb_subcategoria_sub.id_subcategoria_sub'), nullable=False)
    idUsuario = db.Column('id_usuario_eve', db.Integer, db.ForeignKey('comum.tb_usuario_usu.id_usuario_usu'), nullable=False)
    numOcorrencia = db.Column('num_ocorrencia_eve', db.String(11), nullable=False)
    txtProblema = db.Column('txt_problema_eve', db.String(1000), nullable=False)
    txtEndereco = db.Column('txt_endereco_eve', db.String(500), nullable=False)
    txtLat = db.Column('txt_latitude_eve', db.String(20), nullable=False)
    txtLong = db.Column('txt_longitude_eve', db.String(20), nullable=False)
    file = db.Column('img_file_eve', db.LargeBinary, nullable=False)
    dataInicio = db.Column('dat_inicio_eve', db.DateTime, nullable=False)
    dataFim = db.Column('dat_fim_eve', db.DateTime, nullable=True)
    fileBase64 = None
    
    usuario = db.relationship("User")
    subcategoria = db.relationship("Subcategoria")

    def __init__(self, idSubcategoria, idUsuario, numOcorrencia, txtProblema, txtEndereco, txtLat, txtLong, file, dataInicio):
        self.idSubcategoria = idSubcategoria
        self.idUsuario = idUsuario
        self.numOcorrencia = numOcorrencia
        self.txtProblema = txtProblema
        self.txtEndereco = txtEndereco
        self.txtLat = txtLat
        self.txtLong = txtLong
        self.file = file
        self.dataInicio = dataInicio