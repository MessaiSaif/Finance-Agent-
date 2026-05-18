# Présentation de Soutenance : Finance Agent AI

## 1. Introduction au Projet
- **Nom du Projet :** Finance Agent AI
- **Sujet :** Automatisation du traitement des factures et intégration d'un assistant financier intelligent.
- **Objectif :** Remplacer la saisie manuelle des données comptables par une extraction intelligente (Vision + Texte) et offrir une interface conversationnelle (Chatbot) pour interroger les données financières.

---

## 2. Les Différentes Solutions Envisagées

Lors de la phase de conception, plusieurs approches techniques ont été étudiées pour résoudre le problème de l'extraction de données de factures :

### Solution 1 : Approche Classique (OCR + Expressions Régulières + SQL)
- **Principe :** Utiliser un outil comme Tesseract OCR pour lire le texte, puis appliquer des Regex pour trouver les dates, les montants (Total TTC), etc. Les données sont ensuite stockées dans une base de données relationnelle (MySQL/PostgreSQL).
- **Limites :** Extrêmement rigide. Si un fournisseur change la mise en page de sa facture, les règles Regex échouent. De plus, il n'y a pas d'interaction conversationnelle possible.

### Solution 2 : Services Cloud Spécialisés (AWS Textract / Azure Form Recognizer)
- **Principe :** Payer un service Cloud propriétaire pour analyser les documents et renvoyer du JSON.
- **Limites :** Coût récurrent élevé, dépendance totale au fournisseur (Vendor Lock-in), et nécessité de développer toute l'intelligence artificielle de conversation (Agent) de zéro par-dessus ces APIs.

### Solution 3 (Notre Choix) : Modèle LLM Multimodal (Gemini) + Pipeline RAG + Agent IA
- **Principe :** Utiliser les capacités de compréhension visuelle et textuelle de `Gemini` pour l'extraction structurée. Stocker le texte brut dans une base vectorielle locale (`ChromaDB`) pour la recherche sémantique (RAG), et utiliser un Agent IA (`LangChain`) pour interagir avec les données.

---

## 3. Les Avantages de la Solution Choisie

Notre solution (Solution 3) surpasse les autres approches sur plusieurs points cruciaux :

- **Flexibilité et Résilience :** Contrairement à la Solution 1, le LLM comprend sémantiquement ce qu'est un "Total" ou une "TVA". Peu importe la mise en page ou si la facture est un PDF propre ou une photo prise au smartphone, l'extraction réussit.
- **Génération Structurée Native :** En utilisant l'API `with_structured_output(InvoiceData)`, nous forçons l'IA à renvoyer un objet JSON parfait prêt à être sauvegardé, combinant la puissance de l'IA avec la rigueur du code traditionnel.
- **Actionnabilité avec les Outils (Tools) :** Notre Agent n'est pas qu'un simple chatbot. Il est équipé d'outils (Générer Bilan, Chercher Détails, etc.) qu'il peut déclencher de manière autonome pour accomplir des tâches complexes sur demande.

---

## 4. Avantages Concurrentiels de l'Application

Si ce projet devait être commercialisé, voici ses avantages concurrentiels majeurs :

1. **Expérience Utilisateur (UX) Fluide :** Une application "Tout-en-un" (construite avec Streamlit) qui propose un tableau de bord analytique (Market Insights), un module de téléversement (Drag & Drop), et un assistant de chat financier en temps réel.
2. **Recherche Sémantique Avancée (RAG) :** L'utilisateur peut retrouver une facture en décrivant simplement un objet acheté (ex: "Quelle facture contient les ordinateurs portables achetés en mars ?").
3. **Respect de la Vie Privée et Légèreté :** Les bases de données (JSON et ChromaDB) tournent localement sur la machine. L'architecture ne nécessite aucune infrastructure lourde.
4. **Coût Opérationnel Optimisé :** En utilisant les modèles `flash-lite`, l'application offre une latence extrêmement faible tout en consommant très peu de ressources de calcul.
