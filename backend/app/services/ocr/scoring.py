def weighted_sum(logo, layout, color, font):
    """
    Calculate final authenticity score.
    """
    # Weights
    W_LOGO = 0.3
    W_LAYOUT = 0.3
    W_COLOR = 0.2
    W_FONT = 0.2

    score = (logo * W_LOGO) + (layout * W_LAYOUT) + (color * W_COLOR) + (font * W_FONT)
    return round(score, 2)


def classify(score):
    if score > 0.85:
        return "REAL"
    elif score > 0.60:
        return "SUSPICIOUS"
    else:
        return "FAKE"
