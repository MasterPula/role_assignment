import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Person, Week, Assignment
from django.utils.safestring import mark_safe


def index(request):
    weeks = Week.objects.all().order_by('-week_number')
    context = {
        'weeks': weeks,
    }
    return render(request, 'assigner/index.html', context)

def generate_assignments(request):
    if request.method == "POST":
        # Determina il numero della prossima settimana
        last_week = Week.objects.order_by('-week_number').first()
        if last_week:
            next_week_number = last_week.week_number + 1
        else:
            next_week_number = 1

        # Recupera le assegnazioni delle ultime 2 settimane (se esistono)
        recent_weeks = Week.objects.filter(week_number__gte=next_week_number - 2)
        recent_assigned = set()
        for week in recent_weeks:
            for assign in week.assignments.all():
                recent_assigned.add(assign.person.id)

        # Costruisci un dizionario con l'ultimo ruolo assegnato a ogni persona
        last_assignment = {}  # {person_id: role}
        for assign in Assignment.objects.all().order_by('week__week_number'):
            last_assignment[assign.person.id] = assign.role

        assigned_current = set()  # per evitare doppie assegnazioni nella stessa settimana
        assignments_to_create = []
        persons_all = list(Person.objects.all())
        warnings_list = []
        
        # Per ogni ruolo da 2 a 9, seleziona un candidato
        for role in range(1, 6):
            # Partiamo dalle persone non ancora assegnate in questa settimana
            candidates = [p for p in persons_all if p.id not in assigned_current]
            # Escludiamo chi è stato assegnato nelle ultime 2 settimane
            candidates = [p for p in candidates if p.id not in recent_assigned]
            # Escludiamo chi, se già assegnato in passato, ha avuto lo stesso ruolo l'ultima volta
            candidates = [p for p in candidates if last_assignment.get(p.id) != role]

            if candidates:
                chosen = random.choice(candidates)
            else:
                # Se non ci sono candidati che soddisfano i vincoli, segnala un warning e procede in maniera randomica
                warnings_list.append(f"Nessun candidato disponibile per Ruolo {role} che soddisfa i vincoli. Assegnazione randomica.")
                candidates = [p for p in persons_all if p.id not in assigned_current]
                if not candidates:
                    messages.error(request, "Non ci sono abbastanza persone disponibili per assegnare tutti i ruoli.")
                    return redirect('index')
                chosen = random.choice(candidates)
            
            assigned_current.add(chosen.id)
            assignments_to_create.append({'role': role, 'person': chosen})

        # Crea la nuova settimana
        week = Week.objects.create(week_number=next_week_number)
        # Crea le assegnazioni per la settimana corrente
        for assign_data in assignments_to_create:
            Assignment.objects.create(week=week, role=assign_data['role'], person=assign_data['person'])
        
        # Costruisci il testo da mostrare
        message_text = "Buonasera a tutti. Questi sono i servizi per la messa di domani:<br>" + "".join(
            [f"Ruolo {assign_data['role']}: {assign_data['person'].name }<br>" for assign_data in assignments_to_create]
        )

        # Visualizza eventuali warning e il messaggio di successo
        for warn in warnings_list:
            messages.warning(request, warn)
        messages.success(request, f"Assegnazioni per la settimana {next_week_number} generate correttamente. <br><br>{message_text}")
    return redirect('index')
from django.shortcuts import get_object_or_404

def edit_week(request, week_id):
    week = get_object_or_404(Week, id=week_id)
    persons = Person.objects.all()
    
    if request.method == "POST":
        # Aggiorna le assegnazioni in base al form inviato
        for assignment in week.assignments.all():
            new_person_id = request.POST.get(f"assignment_{assignment.id}")
            if new_person_id:
                new_person = Person.objects.get(id=new_person_id)
                assignment.person = new_person
                assignment.save()
        
        # Recupera la lista aggiornata delle assegnazioni per questa settimana
        assignments_list = "".join(
            [f"Posizione {a.role}: {a.person.name}<br>" for a in week.assignments.all()]
        )
        # Costruisci il messaggio completo
        success_message = f"Settimana {week.week_number} aggiornata correttamente."
        full_message = success_message + "<br><br>" + "Buonasera a tutti. Questi sono i servizi per la messa di domani:<br>" + assignments_list
        # Invia il messaggio marcandolo come safe per rendere effettivi gli <br>
        messages.success(request, mark_safe(full_message))
        return redirect('index')
    
    context = {'week': week, 'persons': persons}
    return render(request, 'assigner/edit_week.html', context)
