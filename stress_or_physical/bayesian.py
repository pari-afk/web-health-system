SYMPTOM_CPT = {
    'headaches':             (0.75, 0.45),
    'fatigue':               (0.80, 0.60),
    'chest_tightness':       (0.65, 0.25),
    'nausea':                (0.50, 0.55),
    'vomiting':              (0.20, 0.60),
    'muscle_tension':        (0.75, 0.30),
    'dizziness':             (0.55, 0.50),
    'shortness_of_breath':   (0.60, 0.40),
    'sleep_disturbances':    (0.80, 0.35),
    'stomach_upset':         (0.65, 0.45),
    'racing_heart':          (0.70, 0.30),
    'heart_palpitations':    (0.65, 0.30),
    'brain_fog':             (0.75, 0.30),
    'localized_pain':        (0.30, 0.70),
    'fever_chills':          (0.10, 0.85),
    'swelling':              (0.15, 0.75),
    'sweating':              (0.55, 0.40),
    'trembling':             (0.60, 0.25),
    'skin_issues':           (0.50, 0.40),
    'eye_strain':            (0.60, 0.30),
}

# red flag symptoms 
RED_FLAGS = {'fever_chills', 'swelling', 'vomiting', 'localized_pain', 'shortness_of_breath'}


SIGNAL_EXPLANATIONS = {
    'headaches':           ('Stress signal', 'Headaches are an important symptom of chronic stress and tension.'),
    'fatigue':             ('Stress signal', 'Persistent fatigue is frequently reported in stress and burnout.'),
    'chest_tightness':     ('Stress signal', 'Chest tightness is a common somatic manifestation of anxiety.'),
    'nausea':              ('Mixed signal', 'Nausea can appear in both stress and physical illness.'),
    'vomiting':            ('Physical signal', 'Vomiting is more strongly associated with physical illness.'),
    'muscle_tension':      ('Stress signal', 'Muscle tension is a direct physiological response to stress.'),
    'dizziness':           ('Mixed signal', 'Dizziness can be stress-related or indicate a physical condition.'),
    'shortness_of_breath': ('Mixed signal', 'Shortness of breath can be anxiety-driven or physically caused.'),
    'sleep_disturbances':  ('Stress signal', 'Sleep disruption is strongly linked to stress and anxiety.'),
    'stomach_upset':       ('Stress signal', 'The gut-brain connection makes stomach upset common in stress.'),
    'racing_heart':        ('Stress signal', 'Racing heart is a classic stress and anxiety response.'),
    'heart_palpitations':  ('Stress signal', 'Palpitations are frequently reported in anxiety and acute stress.'),
    'brain_fog':           ('Stress signal', 'Brain fog and poor focus are frequently reported in chronic stress.'),
    'localized_pain':      ('Physical signal', 'Localized pain is more suggestive of a physical cause.'),
    'fever_chills':        ('Physical signal', 'Fever strongly indicates a physical or infectious cause.'),
    'swelling':            ('Physical signal', 'Swelling is a strong indicator of physical illness or injury.'),
    'sweating':            ('Mixed signal', 'Sweating without exertion can be stress or physically driven.'),
    'trembling':           ('Stress signal', 'Trembling is commonly associated with anxiety and stress.'),
    'skin_issues':         ('Mixed signal', 'Skin issues can be stress-triggered or physically caused.'),
    'eye_strain':          ('Stress signal', 'Eye strain is frequently linked to stress and fatigue.'),
}

def run_bayesian(data):
    # prior
    p_stress = 0.5
    p_physical = 0.5

    selected_symptoms = data.getlist('symptoms')
    all_symptoms = list(SYMPTOM_CPT.keys())

    # likelihood of all symptoms
    for symptom in all_symptoms:
        p_s, p_p = SYMPTOM_CPT[symptom]
        if symptom in selected_symptoms:
            p_stress *= p_s
            p_physical *= p_p
        else:
            p_stress *= (1 - p_s)
            p_physical *= (1 - p_p)

    # context 
    timing = data.get('symptom_timing', '')
    if timing == 'work_periods':
        p_stress *= 1.4
    elif timing == 'morning':
        p_stress *= 1.2
    elif timing == 'random':
        p_physical *= 1.2

    duration = data.get('symptom_duration', '')
    if duration == 'few_days':
        p_physical *= 1.2
    elif duration == 'more_than_month':
        p_stress *= 1.3

    seen_doctor = data.get('seen_doctor', '')
    if seen_doctor == 'ruled_out':
        p_stress *= 1.5
    elif seen_doctor == 'no_diagnosis':
        p_stress *= 1.2

    if data.get('better_relaxed') == 'yes':
        p_stress *= 1.4

    if data.get('had_before_stressful') == 'yes':
        p_stress *= 1.3

    if data.get('others_sick') == 'yes':
        p_physical *= 1.5

    activity = data.get('activity_effect', '')
    if activity == 'better':
        p_stress *= 1.2
    elif activity == 'worse':
        p_physical *= 1.2

    # lifestyle
    try:
        stress_level = int(data.get('stress_level', 5))
    except ValueError:
        stress_level = 5
    if stress_level >= 8:
        p_stress *= 1.5
    elif stress_level >= 6:
        p_stress *= 1.2

    sleep = data.get('sleep_quality', '')
    if sleep == 'poor':
        p_stress *= 1.3
    elif sleep == 'good':
        p_physical *= 1.1

    life_events = data.get('life_events', '')
    if life_events == 'significant':
        p_stress *= 1.4
    elif life_events == 'stable':
        p_physical *= 1.1

    overwhelmed = data.get('overwhelmed', '')
    if overwhelmed == 'always':
        p_stress *= 1.4
    elif overwhelmed == 'often':
        p_stress *= 1.2

    if data.get('deadlines') == 'yes':
        p_stress *= 1.2

    if data.get('social_withdrawal') == 'yes':
        p_stress *= 1.2

    appetite = data.get('appetite', '')
    if appetite == 'reduced':
        p_stress *= 1.1
    elif appetite == 'increased':
        p_stress *= 1.1

    # normalize
    total = p_stress + p_physical
    stress_pct = round((p_stress / total) * 100)
    physical_pct = 100 - stress_pct

    # classification
    if stress_pct >= 65:
        classification = 'stress'
        label = 'Likely Stress-Induced'
        summary = (
            'Your symptom pattern, timing, and lifestyle factors align strongly '
            'with stress-induced symptoms. '
            'Stress is also a cause for physical symptoms, and it is recommended that '
            'managing stress levels may provide relief.'
        )
    elif physical_pct >= 65:
        classification = 'physical'
        label = 'Likely Physical'
        summary = (
            'Your symptom pattern points strongly toward a physical cause. '
            'This does not rule out stress entirely, but the combination of symptoms '
            'you reported suggests it may be worth consulting a healthcare provider.'
        )
    else:
        classification = 'mixed'
        label = 'Mixed — Stress and Physical'
        summary = (
            'Your symptoms do not point strongly in either direction. Both stress '
            'and physical factors may be contributing. Consider monitoring your '
            'symptoms and speaking with a healthcare provider if they persist.'
        )


    signals = []
    for symptom in selected_symptoms:
        if symptom in SIGNAL_EXPLANATIONS:
            tag, explanation = SIGNAL_EXPLANATIONS[symptom]
            signals.append({
                'tag': tag,
                'symptom': symptom.replace('_', ' ').title(),
                'explanation': explanation
            })

    # context 
    if timing == 'work_periods':
        signals.append({
            'tag': 'Stress signal',
            'symptom': 'Symptom timing',
            'explanation': 'Symptoms peak during or after high-demand periods. This is a common pattern of stress-induced symptoms.'
        })

    if stress_level >= 8:
        signals.append({
            'tag': 'Stress signal',
            'symptom': f'Self-reported stress of {stress_level}/10',
            'explanation': 'Significantly elevated stress can manifest as physical symptoms.'
        })

    if sleep == 'poor':
        signals.append({
            'tag': 'Stress signal',
            'symptom': 'Less than 6 hours of sleep',
            'explanation': 'Chronic sleep deprivation is a major driver of stress-induced symptoms.'
        })

    if data.get('others_sick') == 'yes':
        signals.append({
            'tag': 'Physical signal',
            'symptom': 'Others around you are sick',
            'explanation': 'When people nearby share similar symptoms, a physical or infectious cause is more likely.'
        })

    # recommendations
    recommendations = []
    if classification == 'stress':
        recommendations = [
            {
                'title': 'Stress management first',
                'body': 'Try a structured stress-reduction technique such as daily diaphragmatic breathing, progressive muscle relaxation, or a short mindfulness practice.',
                'source': 'https://www.mayoclinic.org/healthy-lifestyle/stress-management/basics/stress-basics/hlv-20049495'
            },
            {
                'title': 'Prioritize sleep hygiene',
                'body': 'Set a consistent sleep/wake schedule, reduce screen exposure in the hour before bed, and limit caffeine after 2pm.',
                'source': 'https://www.phac-aspc.gc.ca/hp-ps/hl-mvs/pa-ap/07paap-eng.php'
            },
            {
                'title': 'Talk to a trusted person',
                'body': 'Speaking with a therapist, counsellor, or trusted person about current stressors can often reduce physical symptom burden quickly.',
                'source': 'https://www.mayoclinic.org/diseases-conditions/mental-illness/in-depth/mental-health/art-20046477'
            },
        ]
    elif classification == 'physical':
        recommendations = [
            {
                'title': 'Consult a healthcare provider',
                'body': 'Your symptoms suggest a physical cause that warrants professional evaluation. Please book an appointment with your doctor.',
                'source': 'https://www.canada.ca/en/public-health.html'
            },
            {
                'title': 'Monitor your symptoms',
                'body': 'Please keep track of when symptoms occur, their severity, and any patterns. This will help your doctor make a more accurate assessment.',
                'source': 'https://www.mayoclinic.org'
            },
        ]
    else:
        recommendations = [
            {
                'title': 'Address both possibilities',
                'body': 'Consider speaking with a doctor to rule out physical causes while also evaluating your current stress levels.',
                'source': 'https://www.canada.ca/en/public-health.html'
            },
            {
                'title': 'Track your symptoms',
                'body': 'Note when symptoms are worst and whether they correlate with stressful events or physical activity.',
                'source': 'https://www.mayoclinic.org'
            },
        ]

    # red flag check
    red_flag_symptoms = [s for s in selected_symptoms if s in RED_FLAGS]
    red_flag = len(red_flag_symptoms) > 0

    return {
        'classification': classification,
        'label': label,
        'summary': summary,
        'stress_pct': stress_pct,
        'physical_pct': physical_pct,
        'signals': signals,
        'recommendations': recommendations,
        'red_flag': red_flag,
    }
