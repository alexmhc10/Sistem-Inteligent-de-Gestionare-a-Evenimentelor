import os
import joblib
import numpy as np
from django.conf import settings
from django.core.cache import cache
from base.models import Guests, Menu, MenuRating
import logging

logger = logging.getLogger(__name__)

class LightFMRecommender:
    """
    Clasă pentru integrarea modelului LightFM în aplicația Django
    """
    
    def __init__(self):
        self.model = None
        self.dataset = None
        self.user_features = None
        self.item_features = None
        self.guest_id_to_idx = {}
        self.dish_id_to_idx = {}
        self.guests = []
        self.dishes = []
        self.is_loaded = False
        
    def load_model(self, model_path=None):
        """Încarcă modelul antrenat"""
        if model_path is None:
            model_path = os.path.join(settings.BASE_DIR, 'lightfm_model.pkl')
        
        try:
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.model = model_data['model']
                self.dataset = model_data['dataset']
                self.user_features = model_data['user_features']
                self.item_features = model_data['item_features']
                self.guest_id_to_idx = model_data['guest_id_to_idx']
                self.dish_id_to_idx = model_data['dish_id_to_idx']
                self.guests = model_data['guests']
                self.dishes = model_data['dishes']
                self.is_loaded = True
                logger.info("LightFM model loaded successfully")
                return True
            else:
                logger.warning(f"Model file not found: {model_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading LightFM model: {e}")
            return False
    
    def get_recommendations(self, guest_id, top_n=10, exclude_rated=True):
        """
        Generează recomandări pentru un invitat
        
        Args:
            guest_id: ID-ul invitatului
            top_n: Numărul de recomandări
            exclude_rated: Exclude preparatele deja evaluate
        
        Returns:
            Lista de recomandări cu scoruri
        """
        if not self.is_loaded:
            logger.error("Model not loaded")
            return []
        
        try:
            # Găsește indexul invitatului
            if guest_id not in self.guest_id_to_idx:
                logger.warning(f"Guest {guest_id} not found in model")
                return []
            
            guest_idx = self.guest_id_to_idx[guest_id]
            
            # Generează predicții pentru toate preparatele
            scores = self.model.predict(guest_idx, np.arange(len(self.dishes)))
            
            # Găsește preparatele deja evaluate (dacă exclude_rated=True)
            rated_dish_ids = set()
            if exclude_rated:
                rated_dish_ids = set(MenuRating.objects.filter(
                    guest_id=guest_id
                ).values_list('menu_item_id', flat=True))
            
            # Filtrează și sortează recomandările
            recommendations = []
            for dish_idx, score in enumerate(scores):
                dish_id = list(self.dish_id_to_idx.keys())[
                    list(self.dish_id_to_idx.values()).index(dish_idx)
                ]
                
                # Exclude preparatele deja evaluate
                if exclude_rated and dish_id in rated_dish_ids:
                    continue
                
                # Găsește informațiile despre preparat
                dish_info = next((d for d in self.dishes if d['id'] == dish_id), None)
                if dish_info:
                    recommendations.append({
                        'dish_id': dish_id,
                        'name': dish_info['name'],
                        'category': dish_info['category'],
                        'cuisine': dish_info['cuisine'],
                        'score': float(score),
                        'normalized_score': self._normalize_score(score, scores)
                    })
            
            # Sortează după scor și returnează top_n
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:top_n]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def get_similar_dishes(self, dish_id, top_n=5):
        """
        Găsește preparate similare cu unul dat
        """
        if not self.is_loaded:
            return []
        
        try:
            if dish_id not in self.dish_id_to_idx:
                return []
            
            dish_idx = self.dish_id_to_idx[dish_id]
            
            # Calculează similaritatea cu toate preparatele
            similarities = []
            for other_dish_idx in range(len(self.dishes)):
                if other_dish_idx != dish_idx:
                    # Folosește features pentru a calcula similaritatea
                    similarity = self._calculate_dish_similarity(dish_idx, other_dish_idx)
                    similarities.append((other_dish_idx, similarity))
            
            # Sortează și returnează top_n
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            similar_dishes = []
            for dish_idx, similarity in similarities[:top_n]:
                dish_id = list(self.dish_id_to_idx.keys())[
                    list(self.dish_id_to_idx.values()).index(dish_idx)
                ]
                dish_info = next((d for d in self.dishes if d['id'] == dish_id), None)
                if dish_info:
                    similar_dishes.append({
                        'dish_id': dish_id,
                        'name': dish_info['name'],
                        'category': dish_info['category'],
                        'similarity': float(similarity)
                    })
            
            return similar_dishes
            
        except Exception as e:
            logger.error(f"Error finding similar dishes: {e}")
            return []
    
    def _normalize_score(self, score, all_scores):
        """Normalizează scorul între 0 și 100"""
        min_score = np.min(all_scores)
        max_score = np.max(all_scores)
        if max_score == min_score:
            return 50.0
        return ((score - min_score) / (max_score - min_score)) * 100
    
    def _calculate_dish_similarity(self, dish_idx1, dish_idx2):
        """Calculează similaritatea între două preparate"""
        # Implementare simplă - poate fi îmbunătățită
        dish1 = self.dishes[dish_idx1]
        dish2 = self.dishes[dish_idx2]
        
        similarity = 0
        if dish1['category'] == dish2['category']:
            similarity += 0.3
        if dish1['cuisine'] == dish2['cuisine']:
            similarity += 0.3
        if dish1['diet_type'] == dish2['diet_type']:
            similarity += 0.2
        if dish1['spicy_level'] == dish2['spicy_level']:
            similarity += 0.2
        
        return similarity
    
    def get_model_info(self):
        """Returnează informații despre model"""
        if not self.is_loaded:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "total_guests": len(self.guests),
            "total_dishes": len(self.dishes),
            "model_type": "LightFM",
            "features_shape": self.user_features.shape if self.user_features is not None else None
        }

# Instanță globală pentru cache
_recommender_instance = None

def get_recommender():
    """Returnează instanța singleton a recomandatorului"""
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = LightFMRecommender()
        _recommender_instance.load_model()
    return _recommender_instance

def get_recommendations_for_guest(guest_id, top_n=10, use_cache=True):
    """
    Funcție helper pentru a obține recomandări pentru un invitat
    
    Args:
        guest_id: ID-ul invitatului
        top_n: Numărul de recomandări
        use_cache: Folosește cache pentru performanță
    
    Returns:
        Lista de recomandări
    """
    if use_cache:
        cache_key = f"recommendations_guest_{guest_id}_{top_n}"
        cached_recommendations = cache.get(cache_key)
        if cached_recommendations is not None:
            return cached_recommendations
    
    recommender = get_recommender()
    recommendations = recommender.get_recommendations(guest_id, top_n)
    
    if use_cache:
        cache.set(cache_key, recommendations, 3600)  # Cache pentru 1 oră
    
    return recommendations

def get_similar_dishes_for_dish(dish_id, top_n=5, use_cache=True):
    """
    Funcție helper pentru a găsi preparate similare
    
    Args:
        dish_id: ID-ul preparatului
        top_n: Numărul de preparate similare
        use_cache: Folosește cache pentru performanță
    
    Returns:
        Lista de preparate similare
    """
    if use_cache:
        cache_key = f"similar_dishes_{dish_id}_{top_n}"
        cached_similar = cache.get(cache_key)
        if cached_similar is not None:
            return cached_similar
    
    recommender = get_recommender()
    similar_dishes = recommender.get_similar_dishes(dish_id, top_n)
    
    if use_cache:
        cache.set(cache_key, similar_dishes, 3600)  # Cache pentru 1 oră
    
    return similar_dishes 