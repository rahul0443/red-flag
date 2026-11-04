"""Multilingual set: 6 languages x (3 scams + 3 legitimate). Written by us; links are defanged (hxxp) and refanged by the runner."""
import json
from pathlib import Path

D = {
 "es": ([ "Correos: su paquete está retenido. Pague 1,99 € de tasa de aduana aquí: hxxp://correos-envio-pago.top/pagar",
          "Banco Santander: su cuenta ha sido bloqueada. Verifique su identidad ahora: hxxp://santander-verificacion.xyz/login",
          "Hola abuela, soy tu nieto, tuve un accidente y necesito 800 euros en tarjetas de regalo ya. No le digas a mamá."],
        [ "Mercadona: su pedido nº 4821 se entregará mañana entre las 10:00 y las 12:00. Gracias por su compra.",
          "¿Quedamos mañana a las 6 en la cafetería de siempre?",
          "Iberdrola: su factura de 62,40 € vence el 20 de noviembre. Puede consultarla en su área de cliente."]),
 "hi": ([ "आपका SBI खाता आज बंद हो जाएगा। KYC अपडेट करने के लिए यहां क्लिक करें: hxxp://sbi-kyc-update.top/verify",
          "बधाई हो! आपने 25 लाख रुपये की लॉटरी जीती है। इनाम पाने के लिए 5000 रुपये प्रोसेसिंग फीस जमा करें और किसी को न बताएं।",
          "यह पुलिस विभाग है। आपके आधार कार्ड का उपयोग गैरकानूनी कार्यों में हुआ है। गिरफ्तारी से बचने के लिए तुरंत 20,000 रुपये UPI से भेजें।"],
        [ "आपका ओटीपी 482913 है। इसे किसी के साथ साझा न करें। - HDFC Bank",
          "माँ, मैं शाम को 7 बजे तक घर आ जाऊँगा।",
          "Zomato: आपका ऑर्डर 25 मिनट में पहुँच जाएगा।"]),
 "zh": ([ "【中国邮政】您的包裹因地址不详被扣留,请在24小时内点击链接补充信息并支付2元运费:hxxp://youzheng-express.top/pay",
          "【银行通知】您的账户存在异常登录,请立即登录验证,否则将被冻结:hxxp://icbc-verify-secure.xyz/login",
          "你好,我是你的新朋友,看你的头像很亲切,我们加个微信聊聊吧,我有很好的投资项目带你赚钱。"],
        [ "【顺丰速运】您的快件已由快递柜签收,取件码 5821,请及时取件。",
          "晚上七点老地方吃饭,不见不散!",
          "【国家电网】您本月电费 86.30 元,请于11月25日前缴纳。可通过网上国网APP查询。"]),
 "fr": ([ "La Poste : votre colis est en attente. Réglez 1,99 € de frais de livraison : hxxp://laposte-colis-suivi.top/paiement",
          "Impots.gouv : vous avez droit à un remboursement de 312,40 €. Cliquez ici pour le recevoir : hxxp://impots-remboursement.xyz/form",
          "Maman, c'est moi, j'ai changé de numéro et mon téléphone est cassé. Peux-tu m'envoyer 450 € par virement urgent ? Ne dis rien à papa."],
        [ "Carrefour : votre commande sera prête en drive demain à 17h. Merci !",
          "Tu es dispo pour le déj demain ? On se retrouve à 12h30.",
          "EDF : votre facture de 71,20 € sera prélevée le 12 du mois prochain. Détails dans votre espace client."]),
 "pt": ([ "Correios: sua encomenda está retida. Pague a taxa de R$ 14,90: hxxp://correios-liberacao.top/pagar",
          "Nubank: detectamos acesso suspeito. Confirme seus dados agora: hxxp://nubank-seguranca.xyz/login",
          "Oi vó, sou eu, perdi meu celular e preciso de R$ 1.500 por Pix urgente. Não conta pra ninguém."],
        [ "iFood: seu pedido saiu para entrega e chega em 20 minutos.",
          "Vamos almoçar amanhã às 13h?",
          "Vivo: sua fatura de R$ 99,90 vence dia 15. Consulte no app Meu Vivo."]),
 "ar": ([ "البريد السعودي: شحنتك معلقة. ادفع رسوم 15 ريال لإتمام التسليم: hxxp://spl-shipment-pay.top/track",
          "بنك الراجحي: تم إيقاف حسابك. حدّث بياناتك الآن: hxxp://alrajhi-verify.xyz/login",
          "مبروك! ربحت جائزة 50,000 دولار. أرسل رسوم التحويل 500 دولار بالبطاقات الهدية ولا تخبر أحداً."],
        [ "أمازون: تم شحن طلبك وسيصل غداً بين 2 و5 مساءً.",
          "هل ستأتي إلى عشاء العائلة يوم الجمعة؟",
          "شركة الكهرباء: فاتورتك لهذا الشهر 210 ريال وتستحق في 25 نوفمبر."]),
}
rows = []
for lang, (scams, legit) in D.items():
    for t in scams:
        rows.append({"id": f"ml-{len(rows):03d}", "lang": lang, "label": "scam", "category": "multilingual", "text": t})
    for t in legit:
        rows.append({"id": f"ml-{len(rows):03d}", "lang": lang, "label": "legit", "category": "multilingual", "text": t})
out = Path(__file__).parent / "data" / "multilingual.jsonl"
out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
print(len(rows), "rows ->", out)
