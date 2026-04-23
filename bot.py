from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")


def categorizar_tarefa(texto):
    palavras = texto.lower().split()

    if any(p in palavras for p in ["comprar", "mercado", "supermercado", "feira", "padaria", "absorvente", "pão"]):
        return "🛒 mercado"

    elif any(p in palavras for p in ["estudar", "curso", "ler", "aprender", "python", "ia"]):
        return "📚 conhecimento"

    elif any(p in palavras for p in ["pagar", "conta", "boleto", "dinheiro", "investimento", "pix"]):
        return "💰 finanças"

    elif any(p in palavras for p in ["treino", "consulta", "academia", "correr", "nadar", "farmácia", "menstruei","treinar", "médico", "remédio"]):
        return "💪 saúde"

    else:
        return "📌 geral"
    
def reindexar_tarefas(linhas):
    novas_linhas = []

    for i, linha in enumerate(linhas, start=1):
        partes = linha.strip().split(" | ")

        if len(partes) < 3:
            continue

        categoria = partes[1]
        texto = " | ".join(partes[2:])

        nova_linha = f"[ ] {i} | {categoria} | {texto}\n"
        novas_linhas.append(nova_linha)

    return novas_linhas

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message.text.strip()

    if mensagem == "/ver":
        try:
            with open("tarefas.txt", "r", encoding="utf-8") as arquivo:
                tarefas = arquivo.readlines()

            if not tarefas:
                await update.message.reply_text("📭 Nenhuma tarefa ainda.")
                return

            categorias = {}

            for tarefa in tarefas:
                partes = tarefa.strip().split(" | ")
                if len(partes) < 3:
                    continue

                status_id = partes[0]
                categoria = partes[1]
                texto = " | ".join(partes[2:])

                try:
                    id_tarefa = int(status_id.replace("[ ]", "").replace("[x]", "").strip())
                except:
                    continue

                if categoria not in categorias:
                    categorias[categoria] = []

                categorias[categoria].append((id_tarefa, status_id, texto))

            resposta = "📋 Suas tarefas:\n\n"

            for categoria in sorted(categorias.keys()):
                resposta += f"\n{categoria.upper()}\n"

                itens_ordenados = sorted(categorias[categoria], key=lambda x: x[0])

                for _, status_id, texto in itens_ordenados:
                    resposta += f"{status_id} | {texto}\n"

            resposta += "\n \n"

            await update.message.reply_text(resposta)

        except FileNotFoundError:
            await update.message.reply_text("📭 Nenhuma tarefa ainda.")

    elif mensagem.startswith("/done"):
        try:
            numeros_texto = mensagem.replace("/done", "").strip()
            ids_para_remover = [int(n.strip()) for n in numeros_texto.split(",")]

            with open("tarefas.txt", "r", encoding="utf-8") as arquivo:
                tarefas = arquivo.readlines()

            novas_tarefas = []
            removidas = []

            for tarefa in tarefas:
                partes = tarefa.strip().split(" | ")
                if len(partes) < 3:
                    novas_tarefas.append(tarefa)
                    continue

                status_id = partes[0]
                try:
                    id_tarefa = int("".join(filter(str.isdigit, status_id)))
                except:
                    novas_tarefas.append(tarefa)
                    continue

                if id_tarefa in ids_para_remover:
                    removidas.append(tarefa.strip())
                else:
                    novas_tarefas.append(tarefa)

            novas_tarefas = reindexar_tarefas(novas_tarefas)
            
            with open("tarefas.txt", "w", encoding="utf-8") as arquivo:
                arquivo.writelines(novas_tarefas)

            if not removidas:
                await update.message.reply_text("❌ Nenhuma tarefa válida foi encontrada.")
                return

            resposta = "✅ Concluídas:\n"
            for r in removidas:
                resposta += f"- {r}\n"

            await update.message.reply_text(resposta)

        except:
            await update.message.reply_text("Use: /done 1 ou /done 1,2,3")

    elif mensagem.startswith("/edit"):
        try:
            partes = mensagem.split(" ", 2)

            if len(partes) < 3:
                await update.message.reply_text("Use: /edit ID novo texto")
                return

            id_editar = int(partes[1])
            novo_texto = partes[2]

            tarefas_editadas = reindexar_tarefas(tarefas_editadas)
            with open("tarefas.txt", "r", encoding="utf-8") as arquivo:
                tarefas = arquivo.readlines()

            tarefas_editadas = []
            encontrado = False

            for tarefa in tarefas:
                partes_tarefa = tarefa.strip().split(" | ")

                if len(partes_tarefa) < 3:
                    tarefas_editadas.append(tarefa)
                    continue

                status_id = partes_tarefa[0]
                categoria = partes_tarefa[1]
                texto = partes_tarefa[2]

                id_atual = int("".join(filter(str.isdigit, status_id)))

            if id_atual == id_editar:
                nova_linha = f"[ ] {id_editar} | {categoria} | {novo_texto}\n"
                tarefas_editadas.append(nova_linha)
                encontrado = True
            else:
                tarefas_editadas.append(tarefa)

            if not encontrado:
                await update.message.reply_text("❌ Tarefa não encontrada.")
                return

            with open("tarefas.txt", "w", encoding="utf-8") as arquivo:
                arquivo.writelines(tarefas_editadas)

            await update.message.reply_text(f"✏️ Tarefa {id_editar} atualizada para: {novo_texto}")

        except:
            await update.message.reply_text("Use: /edit ID novo texto")
        
    else:
        try:
            with open("tarefas.txt", "r", encoding="utf-8") as arquivo:
                linhas = arquivo.readlines()
            
        except FileNotFoundError:
            linhas = []
        novo_id = len(linhas) + 1
        categoria = categorizar_tarefa(mensagem)

        linha = f"[ ] {novo_id} | {categoria} | {mensagem}\n"

        with open("tarefas.txt", "a", encoding="utf-8") as arquivo:
            arquivo.write(linha)

        await update.message.reply_text(f"📝 Tarefa salva em {categoria}: {mensagem}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, responder))

print("🤖 Gabot está rodando...")

app.run_polling()