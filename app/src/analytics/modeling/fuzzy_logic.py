import numpy as np

class FuzzyInferenceSystem:
    def __init__(self):
        self.rules = []
        self.output_memberships = {}
        self.input_memberships = {}
        self.input_ranges = {}

    def add_input_variable(self, name, universe, memberships):
        self.input_memberships[name] = memberships
        self.input_ranges[name] = [min(universe), max(universe)]

    def add_output_variable(self, name, universe, memberships):
        self.output_memberships[name] = memberships
        self.output_ranges = [min(universe), max(universe)]

    def add_rule(self, antecedents, consequent):
        self.rules.append({"antecedents": antecedents, "consequent": consequent})

    def _normalize(self, value, variable_name):
        min_val, max_val = self.input_ranges[variable_name]
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val)

    def _triangular_membership(self, x, params):
        a, b, c = params
        if x <= a or x >= c:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a)
        return (c - x) / (c - b)

    def _fuzzify(self, inputs):
        fuzzified_inputs = {}
        for var, value in inputs.items():
            normalized_value = self._normalize(value, var)
            fuzzified_inputs[var] = {}
            for term, params in self.input_memberships[var].items():
                fuzzified_inputs[var][term] = self._triangular_membership(normalized_value, params)
        return fuzzified_inputs

    def _evaluate_rules(self, fuzzified_inputs):
        activated_rules = []
        for rule in self.rules:
            antecedent_degrees = []
            for var, term in rule["antecedents"].items():
                antecedent_degrees.append(fuzzified_inputs[var][term])
            
            # T-norm (AND operator)
            activation_strength = min(antecedent_degrees)
            
            if activation_strength > 0:
                activated_rules.append({
                    "consequent": rule["consequent"],
                    "strength": activation_strength
                })
        return activated_rules

    def _defuzzify_centroid(self, activated_rules):
            universe_min, universe_max = self.output_ranges
            x_points = np.linspace(universe_min, universe_max, 100)
            
            combined_membership = np.zeros_like(x_points, dtype=np.float64)
            
            # Obtenemos el nombre de la única variable de salida, 'recommendation'.
            output_var_name = list(self.output_memberships.keys())[0]

            for rule in activated_rules:
                # Ahora accedemos correctamente a los parámetros de la membresía.
                # Primero con el nombre de la variable y luego con el término.
                consequent_params = self.output_memberships[output_var_name][rule["consequent"]]
                rule_membership = np.array([self._triangular_membership(x, consequent_params) for x in x_points])
                
                # Implicación por 'min' (truncamiento)
                combined_membership = np.maximum(combined_membership, np.minimum(rule_membership, rule["strength"]))

            if np.sum(combined_membership) == 0:
                return 0.0
                
            return np.sum(x_points * combined_membership) / np.sum(combined_membership)

    # def _defuzzify_centroid(self, activated_rules):
    #     universe_min, universe_max = self.output_ranges
    #     x_points = np.linspace(universe_min, universe_max, 100)
        
    #     combined_membership = np.zeros_like(x_points, dtype=np.float64)
        
    #     for rule in activated_rules:
    #         consequent_params = self.output_memberships[rule["consequent"]]
    #         rule_membership = np.array([self._triangular_membership(x, consequent_params) for x in x_points])
            
    #         # Implicación por 'min' (truncamiento)
    #         combined_membership = np.maximum(combined_membership, np.minimum(rule_membership, rule["strength"]))

    #     if np.sum(combined_membership) == 0:
    #         return 0.0
            
    #     return np.sum(x_points * combined_membership) / np.sum(combined_membership)

    def compute(self, inputs):
        # 1. Normalización y Fuzzificación
        fuzzified_inputs = self._fuzzify(inputs)

        # 2. Evaluación de reglas
        activated_rules = self._evaluate_rules(fuzzified_inputs)
        
        # 3. Defuzzificación
        output_value = self._defuzzify_centroid(activated_rules)
        
        return output_value

# --- Ejemplo de uso ---
# if __name__ == "__main__":
#     fis = FuzzyInferenceSystem()

#     # Definición de variables de entrada
#     fis.add_input_variable(
#         "temperatura", 
#         universe=np.arange(0, 101, 1), 
#         memberships={
#             "fria": [0, 0, 40],
#             "templada": [20, 50, 80],
#             "caliente": [60, 100, 100]
#         }
#     )

#     fis.add_input_variable(
#         "humedad", 
#         universe=np.arange(0, 101, 1),
#         memberships={
#             "seca": [0, 0, 50],
#             "normal": [30, 60, 90],
#             "humeda": [70, 100, 100]
#         }
#     )

#     # Definición de variable de salida
#     fis.add_output_variable(
#         "ventilador", 
#         universe=np.arange(0, 101, 1),
#         memberships={
#             "apagar": [0, 0, 25],
#             "bajo": [10, 40, 70],
#             "alto": [50, 80, 100]
#         }
#     )

#     # Definición de reglas
#     fis.add_rule({"temperatura": "fria", "humedad": "seca"}, "apagar")
#     fis.add_rule({"temperatura": "templada", "humedad": "normal"}, "bajo")
#     fis.add_rule({"temperatura": "caliente", "humedad": "humeda"}, "alto")
#     fis.add_rule({"temperatura": "caliente", "humedad": "normal"}, "alto")
#     fis.add_rule({"temperatura": "templada", "humedad": "humeda"}, "alto")

#     # Correr la simulación
#     input_values = {"temperatura": 75, "humedad": 85}
#     recommendation = fis.compute(input_values)

#     print(f"Para una temperatura de {input_values['temperatura']} y una humedad de {input_values['humedad']}, la recomendación para el ventilador es: {recommendation:.2f}%")