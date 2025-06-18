from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from .models import MenuRating, Guests, Menu

def predict_recommendations_for_guest(guest_id, top_k_neighbors=3, top_n_results=5):
    # Pas 1: construim matricea ratingurilor
    all_ratings = MenuRating.objects.all().values('guest_id', 'menu_item_id', 'rating')
    df = pd.DataFrame.from_records(all_ratings)
    ratings_matrix = df.pivot_table(index='guest_id', columns='menu_item_id', values='rating')

    if guest_id not in ratings_matrix.index:
        return Menu.objects.none()  # Invitatul nu a dat ratinguri

    ratings_filled = ratings_matrix.fillna(0)
    similarity_matrix = cosine_similarity(ratings_filled)
    similarity_df = pd.DataFrame(similarity_matrix, index=ratings_filled.index, columns=ratings_filled.index)

    target_similarities = similarity_df.loc[guest_id].drop(index=guest_id)
    top_neighbors = target_similarities.sort_values(ascending=False).head(top_k_neighbors).index.tolist()

    neighbor_ratings = ratings_matrix.loc[top_neighbors]
    weights = target_similarities.loc[top_neighbors]

    weighted_sum = neighbor_ratings.T.dot(weights)
    similarity_sum = np.abs(weights).sum()
    prediction = weighted_sum / similarity_sum if similarity_sum != 0 else weighted_sum

    already_rated = ratings_matrix.loc[guest_id].dropna().index
    prediction = prediction.drop(index=already_rated, errors='ignore')

    # Pas 2: filtrare pe baza preferințelor
    guest = Guests.objects.select_related('profile').prefetch_related('allergens').get(id=guest_id)
    guest_allergen_ids = guest.allergens.values_list('id', flat=True)

    # Meniuri care conțin alergeni sau dietă nepotrivită
    blocked_menus = Menu.objects.filter(
        allergens__in=guest_allergen_ids
    ).union(
        Menu.objects.exclude(diet_type=guest.diet_preference)
    ).values_list('id', flat=True)

    prediction = prediction.drop(index=blocked_menus, errors='ignore')

    # Pas 3: ajustare scor pe baza altor preferințe
    def adjust_score(menu_id, base_score):
        try:
            menu = Menu.objects.get(id=menu_id)
            bonus = 0
            if menu.serving_temp == guest.temp_preference:
                bonus += 0.1
            if menu.spicy_level == guest.spicy_food:
                bonus += 0.1
            if menu.cooking_method and guest.texture_preference and guest.texture_preference in menu.description.lower():
                bonus += 0.1
            return base_score + bonus
        except Menu.DoesNotExist:
            return base_score

    adjusted_scores = {menu_id: adjust_score(menu_id, score) for menu_id, score in prediction.items()}
    sorted_menu_ids = sorted(adjusted_scores, key=adjusted_scores.get, reverse=True)[:top_n_results]

    return Menu.objects.filter(id__in=sorted_menu_ids)
