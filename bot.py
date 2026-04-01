from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8791192036:AAGgsrt90lPDPJM8NZ7b5kKMARTg9po7AFg"

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message.text

    if mensagem == "/ver":
        try:
            with open("tarefas.txt", "r", encoding="utf-8") as arquivo:
                tarefas = arquivo.readlines()

            if not tarefas:
                resposta = "📭 Nenhuma tarefa salva ainda."
            else:
                resposta = "📋 Suas tarefas:\n"
                for i, tarefa in enumerate(tarefas, 1):
                    resposta += f"{i}. {tarefa}"

        except FileNotFoundError:
            resposta = "📭 Nenhuma tarefa salva ainda."

    else:
        with open("tarefas.txt", "a", encoding="utf-8") as arquivo:
            arquivo.write(mensagem + "\n")

        resposta = f"✅ Tarefa salva: {mensagem}"

    await update.message.reply_text(resposta)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, responder))

print("🤖 Gabot está rodando...")

app.run_polling()