#!/usr/bin/env python3
"""
Knowledge Tool - Outil RAG pour accéder à la base de connaissances cycliste
Version complète corrigée sans erreurs BaseTool
"""

import os
from typing import List

try:
    from langchain.tools import BaseTool
    from langchain.schema import Document
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    class BaseTool:
        def __init__(self):
            pass

class CyclingKnowledgeTool(BaseTool):
    """Outil RAG pour accéder à la base de connaissances cycliste"""
    name = "cycling_knowledge"
    description = "Recherche dans la base de connaissances cycliste pour obtenir des informations précises sur les zones, structures et adaptations"
    
    def _run(self, query: str) -> str:
        """Recherche dans la base de connaissances"""
        try:
            # Importer et créer à chaque utilisation pour éviter les problèmes d'attributs
            from core.knowledge_base import KnowledgeBaseManager
            knowledge_manager = KnowledgeBaseManager()
            
            # Recherche simple
            result = knowledge_manager.search_knowledge(query)
            return f"🔍 {result}"
            
        except Exception as e:
            return f"❌ Erreur lors de la recherche: {str(e)}"

class SimpleCyclingKnowledgeTool:
    """Version simplifiée de l'outil knowledge sans dépendances LangChain"""
    
    def __init__(self):
        try:
            from core.knowledge_base import KnowledgeBaseManager
            self.knowledge_manager = KnowledgeBaseManager()
            print("✅ Outil knowledge simplifié initialisé")
        except ImportError:
            self.knowledge_manager = None
            print("⚠️ Knowledge manager non disponible")
    
    def search(self, query: str) -> str:
        """Recherche simple"""
        if self.knowledge_manager:
            return self.knowledge_manager.search_knowledge(query)
        else:
            return "Base de connaissances non disponible"

def create_knowledge_tool():
    """Factory pour créer l'outil approprié"""
    if LANGCHAIN_AVAILABLE:
        try:
            return CyclingKnowledgeTool()
        except Exception as e:
            print(f"⚠️ Erreur création outil LangChain: {e}")
            return SimpleCyclingKnowledgeTool()
    else:
        return SimpleCyclingKnowledgeTool()