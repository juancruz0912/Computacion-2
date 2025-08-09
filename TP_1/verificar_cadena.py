import json
import hashlib
from datetime import datetime
import os

BLOCKCHAIN_FILE = 'blockchain.json'
REPORTE_FILE = 'reporte.txt'

def hash_creator(prev_hash, datos, timestamp):
    datos_str = json.dumps(datos, sort_keys=True, separators=(',', ':'))
    content = f"{prev_hash}{datos_str}{timestamp}".encode()
    return hashlib.sha256(content).hexdigest()

def verificar_blockchain():
    
    if not os.path.exists(BLOCKCHAIN_FILE):
        print(f"❌ Error: No se encuentra el archivo {BLOCKCHAIN_FILE}")
        return False, [], {}
    
    try:
        with open(BLOCKCHAIN_FILE, 'r') as f:
            blockchain = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Error: El archivo {BLOCKCHAIN_FILE} no contiene JSON válido")
        return False, [], {}
    
    if not blockchain:
        print("❌ Error: La blockchain está vacía")
        return False, [], {}
    
    print(f"🔍 Verificando blockchain con {len(blockchain)} bloques...")
    
    bloques_corruptos = []
    
    total_bloques = len(blockchain)
    bloques_con_alerta = 0
    sum_frecuencia = 0
    sum_presion = 0
    sum_oxigeno = 0
    
    for i, bloque in enumerate(blockchain):
        bloque_num = i + 1
        es_corrupto = False
        errores = []
        
        campos_requeridos = ['timestamp', 'datos', 'alerta', 'prev_hash', 'hash']
        for campo in campos_requeridos:
            if campo not in bloque:
                errores.append(f"Campo '{campo}' faltante")
                es_corrupto = True
        
        if es_corrupto:
            bloques_corruptos.append({
                'bloque': bloque_num,
                'errores': errores
            })
            continue
        
        # Recalcular hash
        hash_calculado = hash_creator(bloque['prev_hash'], bloque['datos'], bloque['timestamp'])
        if bloque['hash'] != hash_calculado:
            errores.append(f"Hash incorrecto: esperado {hash_calculado[:16]}..., encontrado {bloque['hash'][:16]}...")
            es_corrupto = True
        
        if es_corrupto:
            bloques_corruptos.append({
                'bloque': bloque_num,
                'errores': errores
            })
        else:
            print(f"✅ Bloque #{bloque_num}: Hash válido")
        
        # Actualizar estadísticas
        if bloque['alerta']:
            bloques_con_alerta += 1
        
        # Acumular datos para promedios
        try:
            sum_frecuencia += bloque['datos']['frecuencia']['media']
            sum_presion += bloque['datos']['presion']['media']
            sum_oxigeno += bloque['datos']['oxigeno']['media']
        except (KeyError, TypeError):
            print(f"⚠️ Advertencia: Datos incompletos en bloque #{bloque_num}")
        
        # Actualizar prev_hash para siguiente iteración
        prev_hash_esperado = bloque['hash']
    
    # Calcular promedios
    estadisticas = {
        'total_bloques': total_bloques,
        'bloques_con_alerta': bloques_con_alerta,
        'promedio_frecuencia': round(sum_frecuencia / total_bloques, 2) if total_bloques > 0 else 0,
        'promedio_presion': round(sum_presion / total_bloques, 2) if total_bloques > 0 else 0,
        'promedio_oxigeno': round(sum_oxigeno / total_bloques, 2) if total_bloques > 0 else 0
    }
    
    es_valida = len(bloques_corruptos) == 0
    return es_valida, bloques_corruptos, estadisticas

def generar_reporte(es_valida, bloques_corruptos, estadisticas):
    
    timestamp_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    reporte_content = f"""REPORTE DE BLOCKCHAIN BIOMÉDICO
    Fecha: {timestamp_reporte}
    
    ESTADÍSTICAS:
    - Total de bloques: {estadisticas['total_bloques']}
    - Bloques con alertas: {estadisticas['bloques_con_alerta']}
    - Porcentaje de alertas: {(estadisticas['bloques_con_alerta']/estadisticas['total_bloques']*100):.1f}%
    
    PROMEDIOS:
    - Frecuencia cardíaca: {estadisticas['promedio_frecuencia']} bpm
    - Presión sistólica: {estadisticas['promedio_presion']} mmHg
    - Saturación de oxígeno: {estadisticas['promedio_oxigeno']}%
    
    INTEGRIDAD:
    - Estado: {'VÁLIDA' if es_valida else 'CORRUPTA'}
    - Bloques corruptos: {len(bloques_corruptos)}
    """

    if bloques_corruptos:
        reporte_content += "\nBLOQUES CORRUPTOS:\n"
        for corrupto in bloques_corruptos:
            reporte_content += f"- Bloque #{corrupto['bloque']}: {', '.join(corrupto['errores'])}\n"

    try:
        with open(REPORTE_FILE, 'w', encoding='utf-8') as f:
            f.write(reporte_content)
        print(f"📝 Reporte guardado en: {REPORTE_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar reporte: {e}")
        return False

def main():
    print("🔍 VERIFICADOR DE BLOCKCHAIN BIOMÉDICO")
    
    es_valida, bloques_corruptos, estadisticas = verificar_blockchain()
    
    print(f"\n📊 RESULTADOS:")
    print(f"{'─' * 30}")
    print(f"Total de bloques: {estadisticas.get('total_bloques', 0)}")
    print(f"Bloques con alerta: {estadisticas.get('bloques_con_alerta', 0)}")
    print(f"Bloques corruptos: {len(bloques_corruptos)}")
    print(f"Estado de la cadena: {'✅ VÁLIDA' if es_valida else '❌ CORRUPTA'}")
    
    
    if bloques_corruptos:
        print(f"\n🚨 BLOQUES CORRUPTOS:")
        print(f"{'─' * 30}")
        for corrupto in bloques_corruptos:
            print(f"Bloque #{corrupto['bloque']}: {', '.join(corrupto['errores'])}")
    
    # Generar reporte
    if generar_reporte(es_valida, bloques_corruptos, estadisticas):
        print(f"\n✅ Verificación completada. Ver {REPORTE_FILE} para detalles.")
    else:
        print(f"\n⚠️ Verificación completada, pero hubo problemas al generar el reporte.")

if __name__ == "__main__":
    main()