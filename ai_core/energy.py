import psutil
import time

class EnergyManager:
    def __init__(self):
        self.battery = psutil.sensors_battery()
        self.metabolic_rate = 1.0 # 1.0 = Full Speed, 0.1 = Hibernation

    def check_vital_signs(self):
        """
        Updates the metabolic rate based on system resources.
        Returns: current_rate (float)
        """
        self.battery = psutil.sensors_battery()
        cpu_usage = psutil.cpu_percent(interval=0.1)

        # 1. Battery Logic (Survival)
        if self.battery:
            if not self.battery.power_plugged:
                if self.battery.percent < 20:
                    print("[Energy] CRITICAL LOW BATTERY. Entering Hibernation.")
                    self.metabolic_rate = 0.1 # Slow pulse
                elif self.battery.percent < 50:
                    self.metabolic_rate = 0.5 # Conservation mode
                else:
                    self.metabolic_rate = 0.8 # Standard mobile
            else:
                self.metabolic_rate = 1.0 # Plugged in = Full Power
        else:
            # Desktop / Server (No Battery)
            self.metabolic_rate = 1.0

        # 2. CPU Throttling (Stealth)
        if cpu_usage > 90:
            print("[Energy] CPU Overheat/Overload detected. Throttling.")
            self.metabolic_rate *= 0.5

        return self.metabolic_rate

    def can_afford_heavy_task(self):
        """
        Returns True if we have enough energy for Training or Mining.
        """
        return self.metabolic_rate > 0.8

if __name__ == "__main__":
    em = EnergyManager()
    print(f"Rate: {em.check_vital_signs()}")
    print(f"Can train? {em.can_afford_heavy_task()}")
