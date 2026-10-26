from pathlib import Path
import httpx,json,re,streamlit as st
LEVEL=1
TOPIC="Utilisation des LLM pour assister le screening des SLR en génie logiciel"
NAMES=["Appel LLM","Plan Pydantic","SearchAgent","DownloadAgent","ScreeningAgent","ExtractionAgent RAG","WritingAgent","QualityAgent","ReviewSupervisor","Application"]
def demo(level):
 r={"topic":TOPIC,"stages":NAMES[:level],"free_text":"RQ1. Les LLM améliorent-ils le rappel du screening ?\nRQ2. Quel contrôle humain reste nécessaire ?"}
 if level>=2:r["plan"]={"questions":[{"id":"RQ1","concepts":["LLM","SLR","screening"]}],"queries":{"scholar":"LLM AND SLR AND screening","ieee":"(LLM AND SLR)","acm":"Abstract:(LLM SLR)"}}
 if level>=3:r["search"]={"agents":["SearchAgent"],"tools":["Scholar","IEEE Xplore","ACM DL"],"identified":5,"unique":3,"trace":[{"tool":"Scholar","found":2},{"tool":"IEEE","found":2},{"tool":"ACM","found":1}]}
 if level>=4:r["downloads"]=[{"paper":"P01","status":"downloaded"},{"paper":"P02","status":"manual_required","instruction":"Télécharger légalement puis déposer P02.pdf"},{"paper":"P03","status":"downloaded"}]
 if level>=5:r["screening"]=[{"paper":"P01","decision":"include","confidence":.92},{"paper":"P02","decision":"uncertain","confidence":.48},{"paper":"P03","decision":"include","confidence":.89}]
 if level>=6:r["evidence"]=[{"paper":"P01","finding":"rappel amélioré","quote":"recall reached 92%","page":4},{"paper":"P03","finding":"rôles spécialisés","quote":"agents collaborate","page":7}]
 if level>=7:r["report"]={"claim":"Les LLM peuvent réduire la charge de screening sous supervision.","citations":["P01","P03"],"limitations":["P02 attend validation humaine"]}
 if level>=8:r["quality"]={"citation_coverage":1.0,"screening_recall":.92,"decision":"human_review","issues":["P02 incertain"]}
 if level>=9:
  r["agents"]=[{"agent":"Question/Plan","mission":"structurer les QR"},{"agent":"SearchAgent","mission":"interroger trois bases"},{"agent":"DownloadAgent","mission":"obtenir légalement les PDF"},{"agent":"ScreeningAgent","mission":"sélectionner"},{"agent":"ExtractionAgent","mission":"extraire les preuves"},{"agent":"WritingAgent","mission":"rédiger"},{"agent":"QualityAgent","mission":"critiquer"}]
  r["handoffs"]=[{"step":i+1,"from":"ReviewSupervisor","to":a["agent"],"message":a["mission"]} for i,a in enumerate(r["agents"])]
  r["state"]={"checkpoint":"R001-step-7.json","next_agent":"HUMAN","reason":"P02 incertain"}
 if level>=10:r["deployment"]={"api":"/review","health":"ok","provider":"ollama ou groq","secrets":".env","trace_id":"R001"}
 return r
if LEVEL==1:
 from main import DECODING_MODE,MAX_OUTPUT_TOKENS,SAMPLING_TEMPERATURE,TOP_P
 from slrresearch.config import Settings,build_model,resolve_decoding
 from slrresearch.research_questions import generate_questions
 settings=Settings()
 decoding=resolve_decoding(DECODING_MODE,SAMPLING_TEMPERATURE,TOP_P,MAX_OUTPUT_TOKENS)
 model_name=settings.ollama_model if settings.provider=="ollama" else settings.groq_model
 st.set_page_config(page_title="SLRResearchAI · TD1",page_icon=":material/science:",layout="wide")
 st.title("TD1 · Du sujet aux questions de recherche")
 st.write("Cette interface réalise **un seul appel LLM** et conserve sa réponse en texte libre.")
 with st.container(border=True):
  st.subheader("Avant de commencer · Ollama ou Groq ?")
  local,remote=st.columns(2)
  with local:
   st.markdown("**Utilisez Ollama si…**")
   st.markdown("- les données doivent rester locales ;\n- vous travaillez hors-ligne ;\n- votre machine peut exécuter le modèle.\n\nAucune clé API, mais installation et calcul locaux.")
  with remote:
   st.markdown("**Utilisez Groq si…**")
   st.markdown("- les données ne sont pas confidentielles ;\n- Internet est disponible ;\n- vous voulez déporter le calcul.\n\nClé personnelle obligatoire, avec quotas possibles.")
  st.info("Règle rapide : confidentialité ou hors-ligne → Ollama ; installation légère et calcul distant → Groq.")
  st.caption("Le choix se fait dans `.env` avec `LLM_PROVIDER=ollama` ou `LLM_PROVIDER=groq`, puis en relançant Streamlit.")
 with st.container(border=True):
  st.subheader("1. Vérifier le moteur")
  c1,c2,c3=st.columns(3)
  c1.metric("Mode configuré","LLM réel")
  c2.metric("Fournisseur",settings.provider.upper())
  c3.metric("Modèle",model_name)
  if settings.provider=="ollama": st.caption(f"Serveur local : {settings.ollama_base_url}")
  else: st.caption("Appel distant Groq · clé lue depuis GROQ_API_KEY")
  if settings.provider=="ollama": st.success("Choix actif : Ollama — le prompt est envoyé au modèle local configuré.")
  else: st.warning("Choix actif : Groq — le prompt est envoyé à une API distante. N'utilisez pas de données confidentielles.")
  d1,d2,d3=st.columns(3)
  d1.metric("Décodage défini dans main.py",decoding.mode)
  d2.metric("Température effective",decoding.temperature)
  d3.metric("Top-p effectif",decoding.top_p)
  st.caption("Modifiez `DECODING_MODE` dans `main.py`, enregistrez, puis relancez cette page. Les paramètres effectifs sont calculés par `resolve_decoding()`. ")
 mode=st.segmented_control("Mode d'exécution",["LLM réel (.env)","Démonstration explicite"],default="LLM réel (.env)")
 with st.form("td1_call"):
  topic=st.text_area("Sujet de la revue",TOPIC,height=100)
  go=st.form_submit_button("Générer les questions",icon=":material/play_arrow:",type="primary")
 if go:
  if mode=="Démonstration explicite":
   st.session_state.td1_result={"mode":"FAKE / DÉMONSTRATION","provider":"fake","model":"réponse prédéfinie","decoding":decoding.mode,"temperature":decoding.temperature,"top_p":decoding.top_p,"latency":0.0,"system_prompt":"Disponible après exécution du code complété.","user_prompt":"Disponible après exécution du code complété.","text":demo(1)["free_text"]}
  else:
   try:
    with st.status("Appel du modèle en cours…",expanded=True) as status:
     st.write(f"Construction du client {settings.provider} / {model_name}")
     result=generate_questions(build_model(settings,decoding),topic,settings.provider)
     st.write("Un appel `model.invoke()` terminé")
     status.update(label="Réponse reçue",state="complete",expanded=False)
    st.session_state.td1_result={"mode":"LLM RÉEL","provider":result.provider,"model":model_name,"decoding":decoding.mode,"temperature":decoding.temperature,"top_p":decoding.top_p,"latency":result.latency_seconds,"system_prompt":result.system_prompt,"user_prompt":result.user_prompt,"text":result.text}
   except Exception as exc:
    st.error(f"Échec de l'appel {settings.provider} : {exc}")
    st.info("Aucun faux résultat n'a été substitué. Vérifiez `.env`, Ollama ou la clé Groq.")
 if result:=st.session_state.get("td1_result"):
  st.divider(); st.subheader("2. Observer la réponse et sa provenance")
  a,b,c,d=st.columns(4)
  a.metric("Décodage",result["decoding"]); b.metric("Température",result["temperature"]); c.metric("Top-p",result["top_p"]); d.metric("Latence",f'{result["latency"]:.2f} s')
  st.caption(f'Modèle : {result["model"]}')
  p1,p2=st.columns(2)
  with p1:
   with st.expander("System Prompt envoyé"):
    st.code(result["system_prompt"],language="text")
  with p2:
   with st.expander("User Prompt envoyé"):
    st.code(result["user_prompt"],language="text")
  with st.container(border=True): st.markdown(result["text"])
  if result["provider"]=="fake": st.warning("Ce résultat est simulé : aucun modèle n'a été appelé.")
  else: st.success("Cette réponse provient d'un appel réel au fournisseur affiché ci-dessus.")
  st.info("Limite constatée : ce texte est lisible, mais pas encore validé ni directement utilisable comme requête scientifique. Ce sera l'objectif du TD2.")
 st.stop()
if LEVEL==2:
 from slrresearch.config import Settings,build_model
 from slrresearch.research_questions import build_zero_shot_prompt,generate_questions
 from slrresearch.search_plan import parse_rq_line,validate_free_text,build_few_shot_prompt,repair_with_llm,validate_questions,build_question_pipeline
 settings=Settings(); model_name=settings.ollama_model if settings.provider=="ollama" else settings.groq_model
 st.set_page_config(page_title="SLRResearchAI · TD2",page_icon=":material/schema:",layout="wide")
 st.title("TD2 · Du zero-shot à la réparation conditionnelle")
 st.write("Le TD2 repart explicitement de l'artefact produit au TD1, puis améliore seulement ce qui pose problème.")
 with st.container(border=True):
  st.subheader("Acquis du TD1 · premier appel LLM en zero-shot")
  st.write("Au TD1, vous avez construit `generate_questions()`. Son prompt contient une instruction et le sujet, mais aucun exemple : c'est du **zero-shot prompting**.")
  st.code(build_zero_shot_prompt(TOPIC),language="text")
  st.caption("L'output de cet appel devient l'entrée de l'étape 1 du TD2. Le TD2 ne repart pas d'un autre problème.")
 with st.container(border=True):
  a,b,c=st.columns(3); a.metric("Fournisseur",settings.provider.upper()); b.metric("Modèle",model_name); c.metric("Contrat","RQ1 / RQ2 / RQ3")
 mode=st.segmented_control("Source des scénarios",["Cas contrôlés du TP","LLM réel (.env)"],default="Cas contrôlés du TP")
 topic=st.text_area("Sujet de la revue",TOPIC,height=90)
 st.session_state.setdefault("tp2_zero_result",None); st.session_state.setdefault("tp2_few_result",None); st.session_state.setdefault("tp2_repaired",None); st.session_state.setdefault("tp2_final",None)
 good="RQ1. Comment les LLM améliorent-ils le rappel du screening ?\nRQ2. Quel contrôle humain doit-il être conservé ?\nRQ3. Quelles métriques évaluent-elles cette amélioration ?"
 cases={"A — zero-shot conforme":good,"B — zero-shot partiellement conforme":"Voici trois questions de recherche potentielles :\nRQ1. Comment les LLM améliorent-ils le rappel du screening ?\nRQ2 - Quel contrôle humain doit-il être conservé ?\nRQ3. Quelles métriques évaluent-elles cette amélioration ?","C — few-shot conforme":good,"D — few-shot partiellement conforme":"RQ1. Comment les LLM améliorent-ils le rappel du screening ?\nRQ2 - Quel contrôle humain doit-il être conservé ?\nRQ3. Quelles métriques évaluent-elles cette amélioration ?"}
 def diagnose_lines(text):
  diagnostics=[]
  for number,line in enumerate((x.strip() for x in text.splitlines() if x.strip()),start=1):
   try:
    record=parse_rq_line(line); diagnostics.append({"ligne":number,"statut":"Acceptée","contenu":line,"raison":f'{record["identifier"]} respecte le contrat'})
   except ValueError:
    diagnostics.append({"ligne":number,"statut":"Rejetée","contenu":line,"raison":"Ne respecte pas la forme RQn. question"})
  return diagnostics
 def diagnose_expected_rqs(text):
  lines=[line.strip() for line in text.splitlines() if line.strip()]
  results=[]
  for identifier in ("RQ1","RQ2","RQ3"):
   candidates=[line for line in lines if re.match(rf"^{identifier}\b",line)]
   if not candidates:
    results.append({"identifier":identifier,"ok":False,"message":"absente","line":"—","record":None}); continue
   try:
    record=parse_rq_line(candidates[0]); results.append({"identifier":identifier,"ok":True,"message":"transformable par regex + Pydantic","line":candidates[0],"record":record})
   except ValueError:
    results.append({"identifier":identifier,"ok":False,"message":"non transformable : séparateur ou syntaxe invalide","line":candidates[0],"record":None})
  return results
 def render_experiment(run,title):
  st.subheader(title)
  with st.container(border=True):
   st.caption(run["source"])
   st.write("1. Prompt envoyé au LLM")
   st.code(run["prompt"],language="text")
   st.write("2. Réponse brute retournée par le LLM")
   st.code(run["text"],language="text",wrap_lines=True)
  st.write("3. Tentative de transformation de chaque RQ")
  rq_columns=st.columns(3)
  for column,item in zip(rq_columns,run["rq_status"]):
   with column:
    if item["ok"]: st.success(f'{item["identifier"]} : réussie et transformable')
    else: st.error(f'{item["identifier"]} : échouée')
    st.code(item["line"],language="text",wrap_lines=True)
    st.caption(item["message"])
    if item["record"]: st.json(item["record"])
  st.write("4. Bilan global")
  if run["error"]:
   st.error("Échec déterministe global : "+run["error"])
   st.dataframe(run["diagnostics"],hide_index=True)
  else:
   st.success("Réussite globale : les trois RQ peuvent être transformées.")
 st.subheader("Étape 1 · Réutiliser l'output TD1")
 st.write("Exécuter le prompt zero-shot acquis, conserver sa réponse, puis la soumettre à regex et Pydantic.")
 scenario_zero=st.selectbox("Cas TD1 à observer",["A — zero-shot conforme","B — zero-shot partiellement conforme"],key="scenario_zero")
 with st.expander("Voir le prompt TD1 pour le sujet courant"):
  try: st.code(build_zero_shot_prompt(topic),language="text")
  except ValueError: st.warning("Saisissez un sujet non vide.")
 if st.button("1 · Exécuter TD1 et valider son output",icon=":material/looks_one:",type="primary",key="stage1"):
  st.session_state.tp2_repaired=None; st.session_state.tp2_final=None
  if mode=="Cas contrôlés du TP": text=cases[scenario_zero]
  else:
   try: text=generate_questions(build_model(settings),topic,settings.provider).text
   except Exception as exc: st.error(str(exc)); text=None
  if text:
   try: records=validate_free_text(text); error=None
   except Exception as exc: records=[]; error=str(exc)
   st.session_state.tp2_zero_result={"stage":1,"source":"TD1 · appel LLM avec prompt zero-shot","prompt":build_zero_shot_prompt(topic),"text":text,"records":records,"error":error,"diagnostics":diagnose_lines(text),"rq_status":diagnose_expected_rqs(text)}
   st.session_state.tp2_few_result=None
   st.rerun()
 if zero:=st.session_state.get("tp2_zero_result"):
  render_experiment(zero,"Résultat de l'appel zero-shot (TD1)")
  st.subheader("Étape 2 · Few-shot + même validation")
  st.write("On conserve le même sujet et le même validateur. Seul le prompt évolue : il contient maintenant des exemples.")
  if mode=="Cas contrôlés du TP":
   scenario_few=st.selectbox("Scénario contrôlé à exécuter",["C — few-shot conforme","D — few-shot partiellement conforme"],key="scenario_few")
   st.info("Expérience reproductible : C garantit une réussite globale ; D garantit que RQ2 échoue malgré le few-shot. Aucun LLM n'est appelé dans ces deux scénarios.")
  else:
   scenario_few=None
   st.warning("Le menu C/D est masqué en mode réel : C et D sont des scénarios pédagogiques prédéfinis, tandis que la réponse du LLM réel n'est pas prédictible. Revenez à « Cas contrôlés du TP » pour les exécuter.")
  if st.button("2 · Exécuter et valider le few-shot",icon=":material/looks_two:",type="primary",key="stage2"):
   st.session_state.tp2_repaired=None; st.session_state.tp2_final=None
   if mode=="Cas contrôlés du TP":
    text=cases[scenario_few]; source=f"TD2 · simulation contrôlée {scenario_few[0]} — aucun appel LLM"
   else:
    try:
     text=str(build_model(settings).invoke(build_few_shot_prompt(topic)).content).strip(); source=f"TD2 · appel LLM réel {settings.provider.upper()} avec prompt few-shot"
    except Exception as exc: st.error(str(exc)); text=None
   if text:
    try: records=validate_free_text(text); error=None
    except Exception as exc: records=[]; error=str(exc)
    st.session_state.tp2_few_result={"stage":2,"source":source,"prompt":build_few_shot_prompt(topic),"text":text,"records":records,"error":error,"diagnostics":diagnose_lines(text),"rq_status":diagnose_expected_rqs(text)}
    st.rerun()
  if few:=st.session_state.get("tp2_few_result"):
   render_experiment(few,"Résultat du nouvel appel few-shot (TD2)")
   if few["error"]: st.warning("Le few-shot améliore généralement le respect du format, mais cette exécution montre qu'il ne le garantit pas.")
   elif mode=="Cas contrôlés du TP": st.success("Le scénario C réussit globalement. Sélectionnez maintenant D et relancez pour observer l'échec garanti de RQ2.")
   else: st.success("Cet appel réel a réussi globalement. Cela ne prouve pas que tous les futurs appels few-shot réussiront.")
 if current:=st.session_state.get("tp2_few_result"):
  if current["stage"]==2 and current["error"]:
   st.warning("Le few-shot a réduit le risque mais ce cas échoue encore. La réparation conditionnelle est maintenant justifiée.")
   st.subheader("Étape 3 · Réparer seulement l'échec résiduel")
   if st.button("3 · Corriger avec le LLM puis revalider",icon=":material/looks_3:",type="primary",key="stage3"):
    if mode=="Cas contrôlés du TP": repaired=good
    else:
     try: repaired=repair_with_llm(build_model(settings),current["text"],current["error"])
     except Exception as exc: st.error(str(exc)); repaired=None
    if repaired:
     try:
      records=validate_free_text(repaired); questions=validate_questions(records); queries=build_question_pipeline().invoke(repaired)
      st.session_state.tp2_final={"text":repaired,"questions":[q.model_dump() for q in questions],"queries":queries}
     except Exception as exc: st.error("La correction reste invalide : "+str(exc))
  elif current["stage"]==2 and not current["error"]:
   if st.button("Transformer sans correction LLM",icon=":material/schema:",type="primary",key="direct_transform"):
    questions=validate_questions(current["records"]); st.session_state.tp2_final={"text":current["text"],"questions":[q.model_dump() for q in questions],"queries":build_question_pipeline().invoke(current["text"])}
 if final:=st.session_state.get("tp2_final"):
  st.success("Texte conforme puis transformation déterministe réussie.")
  st.json(final["questions"])
  st.subheader("Stratégie de recherche booléenne produite par la chaîne LCEL")
  st.caption("LCEL orchestre les fonctions. La requête combine les variantes d'un concept par OR et les concepts différents par AND.")
  for engine,query in final["queries"].items():
   with st.expander(engine.upper(),expanded=engine=="scholar"): st.code(query,language="text",wrap_lines=True)
 st.stop()
st.set_page_config(page_title=f"SLRResearchAI · TP{LEVEL}",page_icon=":material/science:",layout="wide")
PED={
3:{"acquis":"TD2 : stratégie booléenne validée","concept":"Un agent choisit et appelle plusieurs outils de recherche","input":"Requêtes Scholar, IEEE et ACM","action":"SearchAgent → 3 SearchTool → déduplication","output":"Références uniques avec provenance","key":"search","question":"Pourquoi une simple chaîne déterministe ne suffit-elle plus quand il faut choisir des outils ?"},
4:{"acquis":"TP3 : références identifiées et dédupliquées","concept":"Un workflow déterministe applique une politique d'accès légal","input":"Références, URL et statut open access","action":"DownloadAgent → contrôle OA → téléchargement ou demande humaine","output":"PDF disponibles + file de téléchargement manuel","key":"downloads","question":"Pourquoi ne faut-il pas confier la décision de contourner un paywall au LLM ?"},
5:{"acquis":"TP4 : corpus local et documents manquants connus","concept":"Décision assistée, confiance, abstention et human-in-the-loop","input":"Titres, résumés et critères du protocole","action":"ScreeningAgent → score → include/exclude/uncertain","output":"Décisions justifiées et cas à arbitrer","key":"screening","question":"Pourquoi une décision uncertain est-elle préférable à une inclusion inventée ?"},
6:{"acquis":"TP5 : articles inclus après screening","concept":"RAG : retrouver des passages avant de générer une réponse","input":"PDF inclus + question de recherche","action":"pages → chunks → retrieval lexical → extraction LLM → contrôle déterministe","output":"Preuves avec citation et page","key":"evidence","question":"Quelle différence existe entre la mémoire du LLM et une preuve retrouvée dans un PDF ?"},
7:{"acquis":"TP6 : preuves atomiques, sourcées et traçables","concept":"Génération contrainte par les preuves et abstention","input":"RQ + preuves extraites","action":"WritingAgent → plan → synthèse → contrôle des citations","output":"Rapport scientifique sourcé","key":"report","question":"Pourquoi le rédacteur ne doit-il citer que les identifiants présents dans les preuves ?"},
8:{"acquis":"TP7 : premier rapport généré","concept":"Reflection : un agent critique un artefact produit par un autre","input":"Rapport, citations et décisions de screening","action":"QualityAgent → métriques → problèmes → demande de révision","output":"Rapport de qualité et décision humaine","key":"quality","question":"Pourquoi l'auto-évaluation du seul WritingAgent est-elle insuffisante ?"},
9:{"acquis":"TP8 : agents spécialisés et critères qualité","concept":"Orchestration multi-agent par état, handoffs, branches et boucles","input":"État partagé de la revue","action":"Supervisor → agent compétent → contrôle → prochain handoff","output":"Trajectoire complète et état final","key":"state","question":"Quelles conditions doivent arrêter une boucle de révision ?"},
10:{"acquis":"TP9 : système multi-agent exécutable de bout en bout","concept":"Déploiement, secrets, observabilité et interaction humaine","input":"Workflow validé et configuration locale","action":"Streamlit/API → supervisor → agents → trace_id","output":"Application observable et exploitable","key":"deployment","question":"Pourquoi une belle interface ne suffit-elle pas à rendre un système prêt pour la production ?"},
}
meta=PED[LEVEL]
def execute_current(level,real_search=False,pages=None,question=None,real_rag=False):
 if level==6:
  from dataclasses import asdict
  from slrresearch.extraction_agent import chunk_pages,ExtractionAgent,retrieve_relevant_chunks,build_llm_extractor
  pages=pages or ["Les LLM peuvent assister le screening. Le rappel atteint 92 %. La limite principale est le petit corpus évalué."]
  question=question or "Quel rappel est obtenu et quelle limite est signalée ?"
  chunks=chunk_pages(pages,400)
  retriever=lambda all_chunks,rq:retrieve_relevant_chunks(all_chunks,rq,k=4)
  if real_rag:
   from slrresearch.config import Settings,build_model
   settings=Settings(); extractor=build_llm_extractor(build_model(settings,temperature=0)); mode=f"LLM réel · {settings.provider}"
  else:
   extractor=lambda context,rq:{"finding":"Le rappel annoncé atteint 92 %.","quote":"Le rappel atteint 92 %","page":1,"limitation":"petit corpus évalué"}
   mode="Démonstration déterministe"
  selected=retriever(chunks,question)
  evidence=ExtractionAgent(lambda all_chunks,rq:selected,extractor).run("PDF-01",chunks,question)
  previous=demo(5); current=demo(6); current["evidence"]=[asdict(evidence)]
  current["rag_trace"]={"mode":mode,"pages":len(pages),"chunks_created":len(chunks),"chunks_retrieved":len(selected),"retrieved_context":selected}
  return {"previous":previous,"current":current}
 if level not in (3,4): return {"previous":demo(level-1),"current":demo(level)}
 from dataclasses import asdict
 from slrresearch.search_plan import build_question_pipeline
 from slrresearch.search_agent import SearchAgent,SearchTool,build_open_search_tools
 valid_rqs="RQ1. Comment les LLM améliorent-ils le rappel du screening ?\nRQ2. Quel contrôle humain doit-il être conservé ?\nRQ3. Quelles métriques évaluent-elles cette amélioration ?"
 queries=build_question_pipeline().invoke(valid_rqs)
 if level==4:
  if not real_search: return {"previous":demo(3),"current":demo(4)}
  from slrresearch.download_agent import DownloadAgent,DownloadResult
  base_query=queries["scholar"]
  search_result=SearchAgent([build_open_search_tools()[0]]).run({"openalex":base_query},limit=10)
  open_candidates=[p for p in search_result["papers"] if p.open_access and p.url]
  manual_candidates=[p for p in search_result["papers"] if not p.open_access and p.url]
  folder=Path(__file__).resolve().parent/"downloads"
  def fetch_pdf(url):
   response=httpx.get(url,follow_redirects=True,timeout=30,headers={"User-Agent":"SLRResearchAI-course/1.0"}); response.raise_for_status()
   if not response.content.startswith(b"%PDF"): raise ValueError("La ressource retournée n'est pas un PDF")
   return response.content
  downloads=[]
  downloaded_count=0
  for paper in open_candidates:
   if downloaded_count>=3: break
   try:
    item=DownloadAgent(fetch_pdf,folder).run([paper])[0]; downloads.append(item)
    if item.status in {"downloaded","already_downloaded"}: downloaded_count+=1
   except Exception as exc: downloads.append(DownloadResult(paper.id,"download_error",None,str(exc)))
  for paper in manual_candidates[:2]: downloads.extend(DownloadAgent(fetch_pdf,folder).run([paper]))
  previous=demo(3); previous["search"]={"papers":[asdict(p) for p in search_result["papers"]],"trace":search_result["trace"]}
  current=demo(4); current["downloads"]=[asdict(x) for x in downloads]; current["download_folder"]=str(folder)
  return {"previous":previous,"current":current}
 catalog={
  "scholar":[{"id":"S1","title":"LLM-assisted screening for systematic reviews","abstract":"Recall evaluation.","doi":"10.1/shared","url":"https://example.org/p01.pdf","open_access":True}],
  "ieee":[{"id":"I1","title":"LLM-assisted screening for systematic reviews","abstract":"Duplicate result.","doi":"10.1/shared","url":"https://example.org/p01","open_access":False},{"id":"I2","title":"Human oversight in evidence selection","abstract":"Human review.","doi":"10.1/p02","url":"https://example.org/p02","open_access":False}],
  "acm":[{"id":"A1","title":"Agentic evidence synthesis","abstract":"Specialized agents.","doi":"10.1/p03","url":"https://example.org/p03.pdf","open_access":True}],
 }
 def tool_for(engine):
  return SearchTool(engine,lambda query,limit,name=engine:catalog[name][:limit])
 if real_search:
  base_query=queries["scholar"]
  open_queries={name:base_query for name in ("openalex","crossref","semantic_scholar")}
  result=SearchAgent(build_open_search_tools()).run(open_queries,limit=5); queries=open_queries
 else: result=SearchAgent([tool_for(name) for name in queries]).run(queries,limit=20)
 search={"queries_received_from_tp2":queries,"papers":[asdict(p) for p in result["papers"]],"trace":result["trace"],"duplicates_removed":result["duplicates_removed"],"partial_failure":result.get("partial_failure",False)}
 previous=demo(2); previous["plan"]["queries"]=queries
 current=demo(3); current["search"]=search
 return {"previous":previous,"current":current}
st.title(f"TP{LEVEL} · {NAMES[LEVEL-1]}")
st.caption("Du résultat précédent au nouveau concept : observez chaque transformation.")
with st.sidebar:
 st.write(f"Niveau : **{NAMES[LEVEL-1]}**")
 st.caption("La zone principale indique explicitement si l'exécution est simulée ou réelle.")
with st.container(border=True):
 st.subheader(f"Point de départ · {meta['acquis']}")
 st.write(f"**Entrée réutilisée :** {meta['input']}")
 st.info(f"Nouveau besoin : {meta['concept']}")
topic=st.text_area("Sujet conservé tout au long du projet",TOPIC,height=85)
st.session_state.setdefault(f"tp{LEVEL}_error",None)
if LEVEL==3:
 search_mode=st.segmented_control("Mode de recherche",["Démonstration contrôlée (fake explicite)","Recherche réelle — API ouvertes"],default="Démonstration contrôlée (fake explicite)",key="tp3_search_mode")
 if search_mode.startswith("Démonstration"): st.warning("FAKE EXPLICITE : les références viennent d'un catalogue local conçu pour étudier appels d'outils et déduplication.")
 else: st.info("RÉEL : appels réseau vers OpenAlex, Crossref et Semantic Scholar. Les résultats et leur nombre peuvent varier.")
elif LEVEL==4:
 search_mode=st.segmented_control("Mode de téléchargement",["Démonstration contrôlée","Téléchargement réel open access"],default="Démonstration contrôlée",key="tp4_download_mode")
 if search_mode.startswith("Démonstration"): st.warning("SIMULATION : les statuts sont prédéfinis et aucun fichier scientifique réel n'est téléchargé.")
 else: st.info("RÉEL : recherche OpenAlex puis téléchargement de trois PDF open access au maximum dans le dossier downloads/.")
elif LEVEL==6:
 search_mode=st.segmented_control("Mode d'extraction",["Démonstration déterministe","RAG réel — Ollama/Groq"],default="Démonstration déterministe",key="tp6_rag_mode")
 rag_question=st.text_input("Question posée au document","Quel rappel est obtenu et quelle limite est signalée ?",key="tp6_question")
 uploaded_pdf=st.file_uploader("PDF scientifique à analyser (facultatif en démonstration)",type=["pdf"],key="tp6_pdf")
 if search_mode.startswith("Démonstration"):
  st.warning("MODE CONTRÔLÉ : texte local, retriever lexical et extracteur déterministe. Aucun LLM n'est appelé.")
 else:
  st.info("MODE RÉEL : le PDF est découpé, les passages sont retrouvés localement, puis Ollama ou Groq extrait une preuve structurée. `.env` choisit le fournisseur.")
  if uploaded_pdf is None: st.warning("Ajoutez un PDF avant de lancer le mode réel.")
if st.button(f"Exécuter le TP{LEVEL} · {NAMES[LEVEL-1]}",icon=":material/play_arrow:",type="primary",key="run_current"):
 st.session_state[f"tp{LEVEL}_error"]=None
 try:
  real_mode=(LEVEL==3 and search_mode.startswith("Recherche réelle")) or (LEVEL==4 and search_mode.startswith("Téléchargement réel"))
  rag_pages=None; real_rag=LEVEL==6 and search_mode.startswith("RAG réel")
  if real_rag:
   if uploaded_pdf is None: raise ValueError("Sélectionnez un PDF pour le mode RAG réel.")
   from pypdf import PdfReader
   import io
   rag_pages=[page.extract_text() or "" for page in PdfReader(io.BytesIO(uploaded_pdf.getvalue())).pages]
   if not any(page.strip() for page in rag_pages): raise ValueError("Le PDF ne contient aucun texte extractible (document probablement scanné).")
  st.session_state[f"tp{LEVEL}_result"]=execute_current(LEVEL,real_mode,rag_pages,rag_question if LEVEL==6 else None,real_rag)
  st.rerun()
 except NotImplementedError:
  st.session_state[f"tp{LEVEL}_error"]="Complétez le TODO du TP courant avant d'exécuter cette étape."
  st.session_state[f"tp{LEVEL}_result"]=None
 except httpx.HTTPError as exc:
  st.session_state[f"tp{LEVEL}_error"]=f"Recherche réelle indisponible : {exc}. Vérifiez la connexion ou réessayez plus tard."
  st.session_state[f"tp{LEVEL}_result"]=None
 except Exception as exc:
  st.session_state[f"tp{LEVEL}_error"]=f"Exécution impossible : {exc}"
  st.session_state[f"tp{LEVEL}_result"]=None
if execution_error:=st.session_state.get(f"tp{LEVEL}_error"):
 st.error(execution_error)
if pair:=st.session_state.get(f"tp{LEVEL}_result"):
 previous,current=pair["previous"],pair["current"]
 st.subheader("Ce qui se passe réellement dans cette démonstration")
 steps=meta["action"].split(" → ")
 for index,step in enumerate(steps,1): st.write(f"**{index}. {step}**")
 st.subheader("Comparer avant et après")
 left,right=st.columns(2)
 previous_key=PED.get(LEVEL-1,{}).get("key","plan")
 with left.container(border=True):
  st.caption(f"ENTRÉE HÉRITÉE DU TP{LEVEL-1}")
  st.write(meta["acquis"])
  value=previous.get(previous_key,previous.get("plan",previous.get("free_text")))
  if isinstance(value,list): st.dataframe(value,hide_index=True)
  elif isinstance(value,dict): st.json(value)
  else: st.code(str(value),language="text",wrap_lines=True)
 with right.container(border=True):
  st.caption(f"NOUVEL OUTPUT DU TP{LEVEL}")
  st.write(meta["output"])
  value=current.get(meta["key"])
  if isinstance(value,list): st.dataframe(value,hide_index=True)
  else: st.json(value)
 st.subheader("Trace et responsabilités")
 if LEVEL==3:
  st.write("Les requêtes ci-dessous sont la sortie directe de `build_question_pipeline()` du TD2 et l'entrée de `SearchAgent.run()` du TP3.")
  st.json(current["search"]["queries_received_from_tp2"])
  st.write("Chaque ligne confirme quel outil a reçu quelle requête :")
  st.dataframe(current["search"]["trace"],hide_index=True)
  if current["search"].get("partial_failure"):
   failed=[x["tool"] for x in current["search"]["trace"] if x.get("status")!="success"]
   st.warning("Recherche partiellement réussie. Source(s) indisponible(s) : "+", ".join(failed)+". Les résultats des autres sources sont conservés.")
  st.subheader("Articles réellement retournés" if search_mode.startswith("Recherche réelle") else "Articles du catalogue pédagogique")
  papers=current["search"]["papers"]
  if papers:
   st.dataframe(papers,hide_index=True,column_order=["source","title","doi","open_access","url"],column_config={"url":st.column_config.LinkColumn("Lien")})
   st.success(f"{len(papers)} article(s) unique(s) affiché(s).")
  else: st.warning("La recherche a réussi mais n'a retourné aucun article pour cette requête.")
  st.metric("Doublons supprimés",current["search"]["duplicates_removed"])
 elif LEVEL==4:
  downloads=current["downloads"]
  st.subheader("Fichiers produits")
  st.dataframe(downloads,hide_index=True)
  if current.get("download_folder"): st.code(current["download_folder"],language="text")
  for item in downloads:
   item_path=item.get("path")
   if item["status"] in {"downloaded","already_downloaded"} and item_path and Path(item_path).exists():
    path=Path(item_path)
    st.download_button(f'Télécharger {path.name}',data=path.read_bytes(),file_name=path.name,mime="application/pdf",key=f'download_{item.get("paper_id",item.get("paper"))}')
  successful=sum(x["status"] in {"downloaded","already_downloaded"} for x in downloads)
  if successful: st.success(f"{successful} PDF réel(s) disponible(s) dans downloads/.")
  elif search_mode.startswith("Téléchargement réel"): st.warning("Aucun PDF direct n'a pu être récupéré. Consultez les erreurs et les URLs OpenAlex.")
  manual=[x for x in downloads if x["status"]=="manual_required"]
  st.subheader("Actions manuelles requises")
  if manual:
   st.warning(f"{len(manual)} article(s) ne peuvent pas être téléchargés automatiquement. Une intervention humaine légale est nécessaire.")
   for item in manual:
    with st.container(border=True):
     st.error(f'Action humaine · {item.get("paper_id",item.get("paper"))}')
     st.write(item.get("instruction") or "Téléchargez légalement le PDF puis déposez-le dans le dossier downloads/ avec l'identifiant indiqué.")
  else: st.success("Aucune action manuelle n'est requise pour cette exécution.")
 elif LEVEL==5:
  decisions=current["screening"]
  st.subheader("Décisions proposées par ScreeningAgent")
  st.dataframe(decisions,hide_index=True)
  human_queue=[item for item in decisions if item["decision"]=="uncertain" or item["confidence"]<0.8]
  st.session_state.setdefault("tp5_human_decisions",{})
  st.subheader("Arbitrages humains requis")
  if human_queue:
   st.warning(f"{len(human_queue)} décision(s) ne doivent pas être automatisées. Un humain doit choisir include ou exclude.")
   for item in human_queue:
    paper_id=item["paper"]
    with st.container(border=True):
     st.error(f"À arbitrer · {paper_id}")
     st.write(f'Proposition agent : **{item["decision"]}** · confiance {item["confidence"]:.2f}')
     if st.session_state.tp5_human_decisions.get(paper_id):
      st.success(f'Décision humaine finale : {st.session_state.tp5_human_decisions[paper_id]}')
     with st.container(horizontal=True):
      if st.button("Inclure",key=f"include_{paper_id}",icon=":material/check_circle:"):
       st.session_state.tp5_human_decisions[paper_id]="include"; st.rerun()
      if st.button("Exclure",key=f"exclude_{paper_id}",icon=":material/cancel:"):
       st.session_state.tp5_human_decisions[paper_id]="exclude"; st.rerun()
   resolved=sum(item["paper"] in st.session_state.tp5_human_decisions for item in human_queue)
   st.metric("Arbitrages réalisés",f"{resolved}/{len(human_queue)}")
   if resolved==len(human_queue): st.success("La file humaine est entièrement résolue. Le workflow peut continuer.")
   else: st.info("Le workflow reste en attente tant que toutes les décisions humaines ne sont pas renseignées.")
  else: st.success("Aucun arbitrage humain n'est requis.")
 elif LEVEL==6:
  trace=current["rag_trace"]
  st.subheader("Trace réelle du pipeline RAG")
  a,b,c=st.columns(3)
  a.metric("Pages",trace["pages"]); b.metric("Chunks créés",trace["chunks_created"]); c.metric("Chunks retrouvés",trace["chunks_retrieved"])
  st.info(f'Mode exécuté : {trace["mode"]}')
  st.write("Contexte effectivement transmis à l'extracteur")
  st.dataframe(trace["retrieved_context"],hide_index=True)
  st.success("La preuve affichée a franchi le contrôle déterministe : citation présente sur la page annoncée.")
 elif LEVEL==9:
  st.dataframe(current["handoffs"],hide_index=True)
  st.graphviz_chart('digraph{rankdir=LR;S[label="Supervisor"];Q[label="Plan"];A[label="Search"];D[label="Download"];C[label="Screening"];E[label="RAG"];W[label="Writing"];V[label="Quality"];S->Q->A->D->C->E->W->V->S;}')
 else:
  for index,name in enumerate(current["stages"],1): st.write(f"{index}. {name}")
 with st.expander("Voir l'état brut transmis entre composants"): st.json(current)
 st.subheader("Question d'interprétation")
 st.info(meta["question"])
