import random
import math
import numpy as np


class PopulationModel:
    """
    Klasa odpowiedzialna za modelowanie dynamiki populacji wilków na przestrzeni lat.
    Uwzględnia czynniki takie jak wskaźnik urodzeń, śmiertelności, presję łowiecką
    oraz dostępność zasobów pokarmowych.
    """
    def __init__(self):
        self.years = [2000, 2001, 2002, 2005, 2007, 2010, 2015, 2019, 2020]
        # self.avg_pop = [100, 82, 65, 15, 15, 35, 30, 45, 40, 45]
        self.avg_pop = [100, 125, 150, 108, 102, 104, 125, 145, 145]
        self.growth_rate = None
        self.annual_changes = []
        self.death_rate = 1.0
        self.birth_rate = 1.0
        self.food_access = 1.0
        self.hunting = 1
        self.steps_in_year = 72

        self.calculate_annual_changes()
        self.population = self.calculate_population(self.avg_pop[0])

    def calculate_annual_changes(self):
        """
        Oblicza roczne zmiany populacji na podstawie przekazanych danych.
        """
        for i in range(len(self.years) - 1):
            start_year = self.years[i]
            end_year = self.years[i + 1]
            start_population = self.avg_pop[i]
            end_population = self.avg_pop[i + 1]

            annual_change = (end_population - start_population) / (end_year - start_year)

            for _ in range(start_year, end_year):
                self.annual_changes.append(round(annual_change))

    def calculate_population(self, init_pop):
        """
        Oblicza populacje dla lat 2000-2020 na podstawie obliczonych rocznych zmian.
        """
        new_pop = [init_pop]
        for i in range(20):
            new_avg_pop = new_pop[i] + self.annual_changes[i]
            new_pop.append(round(new_avg_pop))
        return new_pop

    def calculate_growth_rate(self, avg_pop, years):
        """
        Oblicza tempo wzrostu dla modelu logistycznego populacji.
        """
        data = sorted(zip(years, avg_pop))
        years_sorted, pop_sorted = zip(*data)

        k = max(pop_sorted)

        p0 = pop_sorted[0]
        t0 = years_sorted[0]

        pt = pop_sorted[1]
        t = years_sorted[1] - t0

        if pt == p0:
            raise ValueError("The second population value must differ from the initial population.")

        r = -np.log((k - pt) / (pt * (k - p0))) / t
        return r

    def predict_for_next_year(self, year):
        """
        Oblicza przyszlą populację na podstawie logistycznego modelu populacji.
        """
        if self.growth_rate is None:
            self.growth_rate = self.calculate_growth_rate(self.avg_pop, self.years)
        k = 150
        r = self.growth_rate

        # current_population = sum(agent.wolf_count for agent in model.schedule)
        current_population = self.population[-1]

        if current_population >= k:
            predicted_population = k
            print(f"Population capped at 150 for {year}.")
        else:
            predicted_population = current_population + r * current_population * (1 - current_population / k)
            print(f"Predicted population for {year}: {predicted_population}")

        self.years.append(year)
        self.population.append(round(predicted_population))
        self.annual_changes.append(round(predicted_population - current_population))

    def count_wolves(self, model):
        """
        Zlicza wszystkie wilki w modelu.
        """
        wolves = sum(agent.wolf_count for agent in model.schedule)
        return wolves

    def get_new_population(self, year):
        """
        Zwraca populację na dany rok.
        """
        year = year - 2000
        if year in range(20):
            new_population = self.population[year + 1]
        else:
            if len(self.population) < year:
                self.predict_for_next_year(self.years[-1] + 1)
            new_population = self.population[-1]

        return new_population

    def get_hunting_influence(self, population):
        """
        Zwraca populację po uwzględnieniu wpływu myślistwa.
        """
        influence = (
            1 + (self.hunting * 0.05 if self.hunting < 1 else -self.hunting * 0.05 if self.hunting > 1 else 0)
        )

        altered_population = population * influence
        killed_wolves = random.randint(0, 5)
        if altered_population < population:
            killed_wolves = math.ceil(population - altered_population)
        return altered_population, killed_wolves

    def update_population(self, model, year, step):
        """
        Aktualizuje liczbę wilków na siatce.
        """
        new_population = self.get_new_population(year)
        new_population, killed_wolves = self.get_hunting_influence(new_population)
        wolf_count = self.count_wolves(model)

        food_change = int((self.food_access * 10) % 10)
        total_wolves = 1

        if self.food_access > 1:
            total_wolves = 1 + (food_change * 0.02)
        elif self.food_access < 1:
            total_wolves = 1 - (food_change * 0.02)

        delta = self.calculate_delta(model, new_population * total_wolves)
        # print(f"DELTA: {delta}")

        birth_time = self.steps_in_year // 12 * 4
        if step in range(birth_time - 1, birth_time + 1):
            print("birth time")
            self.handle_births(model, delta)

        death_start, death_end = self.steps_in_year // 12 * 11, self.steps_in_year // 12 * 2
        if step >= death_start or step <= death_end:
            if wolf_count < 150 or self.death_rate > 1:
                delta = delta * self.death_rate
            self.handle_deaths(model, delta)

        model.schedule = [agent for agent in model.schedule if agent.wolf_count > 0]

        return killed_wolves

    def calculate_delta(self, model, target_population):
        """
        Oblicza różnicę między aktualną populacją
        a populacją docelową na dany rok.
        """
        current_population = sum(agent.wolf_count for agent in model.schedule)
        delta = target_population - current_population
        return delta

    def handle_births(self, model, delta):
        """
        Zwiększa liczbę wilków podczas okresu narodzin.
        Uwzględnia parametr birth_rate, aby znacząco wpływać na liczbę narodzin.
        """
        # Wybieramy agentów, którzy mogą się rozmnażać (mają więcej niż 2 wilki w grupie)
        eligible_agents = [i for i, agent in enumerate(model.schedule) if agent.wolf_count > 2]
        if eligible_agents:
            agents_to_update = max(1, round(len(eligible_agents) * self.birth_rate))
            selected_agents = random.sample(eligible_agents, min(agents_to_update, len(eligible_agents)))

            for agent in selected_agents:
                wolves_to_add = random.randint(round(2 * self.birth_rate), round(6 * self.birth_rate))
                # wolves_to_add = round(base_births * self.birth_rate)
                model.schedule[agent].wolf_count += wolves_to_add

                if model.schedule[agent].wolf_count > 10:
                    model.split_large_packs()

                delta -= wolves_to_add

                if delta < 0:
                    break

            if delta > 0:
                self.handle_births(model, delta)

    def handle_deaths(self, model, delta):
        """
        Zmniejsza liczbę wilków w okresie zimowym.
        """
        if delta < 0:
            # Skalowanie delta w zależności od birth_rate
            delta = delta * (1 - (self.birth_rate - 1))

            model.schedule.sort(key=lambda agent: agent.wolf_count)

            for agent in model.schedule:
                if delta >= 0:
                    break

                if agent.wolf_count <= 2:  # najpierw usuwamy pojedyncze wilki
                    wolf_change = min(agent.wolf_count, abs(math.ceil(delta // 2)))
                    print(f"-{wolf_change} from small pack")

                    agent.wolf_count -= wolf_change
                    delta += wolf_change
                    model.update_agents()

            while delta < 0:
                wolf_change = random.randint(0, math.ceil(abs(delta // 2)))
                print(-wolf_change)

                while wolf_change > 10:
                    wolf_change = wolf_change // 2

                pack_change = random.randint(0, len(model.schedule) - 1)
                model.schedule[pack_change].wolf_count -= wolf_change

                delta += wolf_change
                model.update_agents()

            if delta < 0:
                self.handle_deaths(model, delta)

