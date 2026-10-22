# Integración experimental TradingAgents ↔ SENTINELA R22

**Rama independiente:** \`sentinela-r22-mcp-lab\`. No modifica \`main\`.

## Estado real
El fork de TauricResearch/TradingAgents se conserva bajo \`ingenierokale/TradingAgents\` y respeta su licencia Apache-2.0. Este directorio añade **una interfaz de intercambio propia**; no es todavía una conexión de agentes LLM de TradingAgents a SENTINELA ni una modificación del motor de órdenes.

SENTINELA R22 dispone de \`tools/auditar_multiagente_r22.py\`, que produce \`reports_v6/mcp_multiagente_lab/SENTINELA_MULTIAGENTE_REPORTE.json\` a partir de ADN SQLite y de los diarios de evidencia del bróker.

## Puente disponible
\`integrations/sentinela_r22/bridge.py\` lee ese reporte JSON de auditoría y produce un resumen sin datos de órdenes individuales, ni credenciales, ni facultad de comprar. Solo contabiliza WIN/LOSS/DRAW cuando el auditor R22 los ha clasificado como verificados.

Ejemplo desde una copia local de este fork:

\`\`\`powershell
python integrations/sentinela_r22/bridge.py --input "C:\SENTINELA\reports_v6\mcp_multiagente_lab\SENTINELA_MULTIAGENTE_REPORTE.json" --output "C:\SENTINELA\reports_v6\mcp_multiagente_lab\tradingagents_snapshot.json"
python -m unittest discover -s integrations/sentinela_r22/tests
\`\`\`

La ruta \`C:\SENTINELA\` es ilustrativa: sustitúyela por tu carpeta real.

## Próximas fases pendientes (NO implementadas)
1. Adaptador de datos para velas M1 OTC con timestamps de proveedor comprobables.
2. Ejecución diferida de agentes de investigación sin afectar la decisión C → C+1.
3. Aprendizaje supervisado sobre liquidaciones verificadas, con partición cronológica prospectiva.
4. Comparación del sistema original contra el multiagente por activo y período, conservando métricas de latencia.
5. Revisión de privacidad antes de enviar eventos ADN a cualquier API LLM.

## Reglas invariantes
- Autoridad de compra **exclusiva del motor determinista de SENTINELA**.
- La entrada C+1 nunca espera a un agente LLM.
- Una señal no equivale a una compra aceptada; tampoco a un WIN.
- No publicar archivos \`.env\`, credenciales Exnova ni telemetría personal.
- Los filtros exploratorios A/B de 24 velas y EMA21 no son un predictor validado ni un veto automático.

Proyecto fuente y atribución: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents), Apache-2.0. Se mantiene la licencia original de TradingAgents.
