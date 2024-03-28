import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import numpy as np
from scipy.io import wavfile
import os
from scipy import signal
import random


class NoiseGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Atomiste Noise Wall Generator")
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        # Entry fields for length, seed, and number of samples
        self.length_label = ttk.Label(root, text="Length (seconds):")
        self.length_label.grid(row=0, column=0, padx=10, pady=5)
        self.length_entry = ttk.Entry(root)
        self.length_entry.insert(60, "60")  # Set default value to 60
        self.length_entry.grid(row=0, column=1, padx=10, pady=5)

        self.seed_label = ttk.Label(root, text="Seed (0 for random):")
        self.seed_label.grid(row=1, column=0, padx=10, pady=5)
        self.seed_entry = ttk.Entry(root)
        self.seed_entry.insert(0, "0")  # Set default value to 0
        self.seed_entry.grid(row=1, column=1, padx=10, pady=5)

        self.samnum_label = ttk.Label(root, text="Number of samples to generate:")
        self.samnum_label.grid(row=2, column=0, padx=10, pady=5)
        self.samnum_entry = ttk.Entry(root)
        self.samnum_entry.insert(3, "3")  # Set default value to 3
        self.samnum_entry.grid(row=2, column=1, padx=10, pady=5)

        # Checkboxes for effects
        self.effects_frame = ttk.Frame(root)
        self.effects_frame.grid(row=3, columnspan=2, padx=10, pady=10)
        self.granular_synthesis_var = tk.BooleanVar(value=True)  # Checked by default
        self.granular_synthesis_check = ttk.Checkbutton(self.effects_frame, text="Apply Granular Synthesis - I recommend you keep this checked, also mandatory for presets", variable=self.granular_synthesis_var)
        self.granular_synthesis_check.pack(anchor='w')

        # Dropdown for granular synthesis presets
        self.preset_label = ttk.Label(root, text="Granular Synthesis Presets:")
        self.preset_label.grid(row=4, column=0, padx=10, pady=5)
        self.preset_var = tk.StringVar(value="regular")  # Default preset
        self.presets = {
            "regular": {"pitch": (0.5, 2.0), "time": (0.5, 2.0), "amp": (0.5, 2.0)},
            "unpredictable": {"pitch": (0.1, 15.0), "time": (0.1, 15.0), "amp": (0.1, 15.0)},
            "very unpredictable": {"pitch": (0.001, 100.0), "time": (0.001, 100.0), "amp": (0.001, 100.0)},
            "bitcrushed": {"pitch": (10.0, 100.0), "time": (0.001, 0.3), "amp": (10.0, 50.0)},
            "bitcrushed to death": {"pitch": (50.0, 1000.0), "time": (0.001, 0.05), "amp": (100.0, 500.0)},
            "deep drone": {"pitch": (0.01, 0.1), "time": (20.0, 100.0), "amp": (0.5, 2.0)},
            "deep and grainy": {"pitch": (10.0, 20.0), "time": (10.0, 30.0), "amp": (0.001, 0.01)},
            "harsh noise wall": {"pitch": (0.1, 1.0), "time": (0.1, 1.0), "amp": (20.0, 200.0)}
        }
        self.preset_dropdown = ttk.OptionMenu(root, self.preset_var, "regular", *self.presets.keys())
        self.preset_dropdown.grid(row=4, column=1, padx=10, pady=5)
                # Default preset
        self.selected_preset = "Regular"

        # Checkboxes for other effects
        self.filter_var = tk.BooleanVar()
        self.stereo_panning_var = tk.BooleanVar()
        self.time_varying_filters_var = tk.BooleanVar()
        self.convolution_reverb_var = tk.BooleanVar()
        self.do_merge = tk.BooleanVar()

        self.filter_check = ttk.Checkbutton(self.effects_frame, text="Apply Random EQ Filters - Low-pass / High-pass / Random frequency spikes and ducks", variable=self.filter_var)
        self.filter_check.pack(anchor='w')
        self.stereo_panning_check = ttk.Checkbutton(self.effects_frame, text="Apply Random Stereo Panning - Especially useful if you plan on merging multiple samples", variable=self.stereo_panning_var)
        self.stereo_panning_check.pack(anchor='w')
        self.convolution_reverb_check = ttk.Checkbutton(self.effects_frame, text="Apply Random 'Smoothing' Function - Don't really know how to explain this one just try it", variable=self.convolution_reverb_var)
        self.convolution_reverb_check.pack(anchor='w')
        self.do_merge_check = ttk.Checkbutton(self.effects_frame, text="Merge the samples in one file - Only check if generating multiple samples", variable=self.do_merge)
        self.do_merge_check.pack(anchor='w')

        # Button to generate noise
        self.generate_button = ttk.Button(root, text="Generate Noise", command=self.generate_noise)
        self.generate_button.grid(row=7, columnspan=1, padx=10, pady=10)

        # Directory selection button
        self.directory_label = ttk.Label(root, text="Select Directory:")
        self.directory_label.grid(row=6, column=0, padx=10, pady=5)
        self.directory_button = ttk.Button(root, text="Browse", command=self.select_directory)
        self.directory_button.grid(row=6, column=1, padx=10, pady=5)
        self.selected_directory = ""

        # Text zone for guidelines
        self.guidelines_label = ttk.Label(root, text="Your best friend for everything noise related! Whether you want to use it as asample machine\nor want to get lucky with your noise wall needs, we have it covered!Note that some generations may take\nlonger depending on the selected effects and other random things happening during the generation.\nHave fun!")
        self.guidelines_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def select_directory(self):
        self.selected_directory = filedialog.askdirectory()
        # You can use 'directory' to save your files or perform other operations

    def update_preset(self, *args):
        self.selected_preset = self.preset_var.get()

    def close_window(self):
        self.root.destroy()

    def toggle_granular_synthesis(self):
        if self.granular_synthesis_var.get():
            self.presets_combobox.config(state="readonly")
        else:
            self.presets_combobox.config(state="disabled")

    def select_preset(self, event):
        self.selected_preset = self.presets_combobox.get()

    def close_window(self):
        self.root.destroy()

    def generate_noise(self):
        length = int(self.length_entry.get())
        length = length
        seed = int(self.seed_entry.get())
        samnum = int(self.samnum_entry.get())
        do_merge = int(self.do_merge.get())
        selected_preset = self.preset_var.get()

        if not self.selected_directory:
            messagebox.showwarning("Warning", "Please select a directory to save the generated files.")
            return

        if seed == 0:
            np.random.seed()
            seed = np.random.randint(1, 999999999)  # Generate a random seed if seed is 0
            merged_seed = seed
        else:
            np.random.seed(seed)
        noises = []
        for i in range(samnum):
            noise = self.generate_basic_noise(length)

            # Apply selected effects
            if self.granular_synthesis_var.get():
                noise = self.apply_granular_synthesis(noise, seed, selected_preset)
            if self.filter_var.get():
                noise = self.apply_filters(noise, seed)
            if self.stereo_panning_var.get():
                noise = self.apply_stereo_panning(noise, seed)
            if self.convolution_reverb_var.get():
                noise = self.apply_convolution_reverb(noise, seed)

            max_abs = np.max(np.abs(noise))
            if max_abs > 0:
                noise_normalized = noise / max_abs
            else:
                noise_normalized = noise  # Avoid division by zero if 'noise' is all zeros

            # Convert the normalized 'noise' array to 16-bit integer format
            noise_int16 = (noise_normalized * 32767).astype(np.int16)
            noises.append(noise_int16)

            # Save noise to file
            file_path = f"{self.selected_directory}/noise_{seed}_{i}.wav"
            wavfile.write(file_path, 44100, noise_int16)

        if seed == 0:
            seed_for_filename = merged_seed
        else:
            seed_for_filename = seed

        if do_merge == 1:
            self.average_and_save(noises, seed_for_filename)

    def generate_basic_noise(self, length):
        return np.random.rand(int(44100 * length))  - 1

    def apply_filters(self, noise, seed):
        # Apply random filters
        np.random.seed(seed)  # Set seed for reproducibility
        filter_type = random.choice(['lowpass', 'highpass', 'middlepass'])
        strength = random.uniform(0.2, 0.8)  # Adjusted range to reduce extremes
        center_frequency = random.uniform(500, 10000)  # Adjusted range for broader frequency coverage

        if filter_type == 'lowpass':
            b, a = signal.butter(4, center_frequency, 'low', fs=44100, output='ba')
        elif filter_type == 'highpass':
            b, a = signal.butter(4, center_frequency, 'high', fs=44100, output='ba')
        else:
            b_high, a_high = signal.butter(4, center_frequency, 'high', fs=44100, output='ba')
            b_low, a_low = signal.butter(4, center_frequency * 2, 'low', fs=44100, output='ba')
            b, a = b_low * strength + b_high * (1 - strength), a_low * strength + a_high * (1 - strength)

        return signal.lfilter(b, a, noise)

    def apply_stereo_panning(self, noise, seed):
        # Apply stereo panning
        np.random.seed(seed)  # Set seed for reproducibility
    
        # Generate random parameters for panning amount and frequency bands
        panning_amount = random.uniform(0, 1)
        frequency_band = random.uniform(100, 10000)

        # Generate panning signals for left and right channels
        panning_signal_left = np.sin(2 * np.pi * frequency_band * np.arange(len(noise)))
        panning_signal_right = np.cos(2 * np.pi * frequency_band * np.arange(len(noise)))

        # Interpolate panning signals for each sample in the noise signal
        panning_left = np.interp(np.linspace(0, len(noise) - 1, len(noise)), np.arange(len(noise)), panning_signal_left) * panning_amount
        panning_right = np.interp(np.linspace(0, len(noise) - 1, len(noise)), np.arange(len(noise)), panning_signal_right) * (1 - panning_amount)

        # Apply panning to the left and right channels of the noise signal
        noise_left = noise * panning_left
        noise_right = noise * panning_right

        # Combine left and right channels to produce stereo output
        noise_stereo = np.vstack((noise_left, noise_right)).T

        return noise_stereo

    def apply_granular_synthesis(self, noise, seed, selected_preset):
        # Apply granular synthesis
        np.random.seed(seed)  # Set seed for reproducibility

        # Generate random parameters for grain size, overlap amount, pitch shift, time stretch, and amplitude variation
        grain_size = random.randint(100, 1000)
        overlap_amount = random.uniform(0.1, 0.5)  # Adjusting the overlap amount

        # Check for division by zero
        if grain_size == 0 or overlap_amount == 0:
            raise ValueError("Grain size and overlap amount cannot be zero")

        # Selecting parameters based on the preset
        if selected_preset in self.presets:
            preset_params = self.presets[selected_preset]
            pitch_shift = random.uniform(*preset_params["pitch"])
            time_stretch = random.uniform(*preset_params["time"])
            amplitude_variation = random.uniform(*preset_params["amp"])
        else:
            # Default parameters if preset not found
            pitch_shift = random.uniform(0.5, 2.0)
            time_stretch = random.uniform(0.5, 2.0)
            amplitude_variation = random.uniform(0.5, 2.0)

        # Initialize granular synthesis parameters
        num_grains = int(len(noise) / (grain_size * (1 - overlap_amount)))  # Adjusting for overlap
        granular_noise = np.zeros_like(noise)

        # Apply granular synthesis to the noise signal
        for i in range(num_grains):
            start_idx = int(i * grain_size * (1 - overlap_amount))  # Adjusting for overlap
            end_idx = min(start_idx + grain_size, len(noise))

            # Extract the current grain
            grain = noise[start_idx:end_idx]

            # Apply pitch shift, time stretch, and amplitude variation to the current grain
            grain_resampled = signal.resample(grain, int(len(grain) * time_stretch))
            grain_resampled = grain_resampled * pitch_shift
            grain_resampled = grain_resampled * amplitude_variation

            # Expand the resampled grain to match the original size
            expanded_grain = np.repeat(grain_resampled, (end_idx - start_idx + len(grain_resampled) - 1) // len(grain_resampled), axis=0)
            expanded_grain = expanded_grain[:end_idx - start_idx]

            # Ensure that the expanded grain has the correct shape
            if len(expanded_grain) < end_idx - start_idx:
                expanded_grain = np.pad(expanded_grain, ((0, end_idx - start_idx - len(expanded_grain)), (0, 0)), mode='constant')

            granular_noise[start_idx:end_idx] += expanded_grain

        return granular_noise

    def apply_convolution_reverb(self, noise, seed):
        # Apply convolution reverb
        np.random.seed(seed)  # Set seed for reproducibility

        # Generate random parameters for the reverb size and intensity
        reverb_size = random.randint(100, 1000)
        reverb_intensity = random.uniform(0.3, 2.05)

        # Generate a simple reverb kernel
        reverb_kernel = np.ones(reverb_size) / reverb_size

        # Ensure the input noise is one-dimensional
        noise = np.ravel(noise)

        # Apply convolution reverb to the noise signal
        reverb = np.convolve(noise, reverb_kernel, mode='same') * reverb_intensity
    
        return reverb

    def average_and_save(self, noises, seed_for_filename, merge_operation='additive'):
        length = int(self.length_entry.get()) * 44100
        combined_noise = np.zeros(length)
    
        for noise in noises:
            # Ensure noise has a compatible shape with combined_noise
            if noise.shape != combined_noise.shape:
                # Resize noise to match the shape of combined_noise
                noise = np.resize(noise, combined_noise.shape)
        
            # Perform the merge operation
                combined_noise += noise

        # Clip combined_noise to prevent overflow
        combined_noise = np.clip(combined_noise, -32768, 32767)

        # Normalize the combined noise
        max_abs = np.max(np.abs(combined_noise))
        if max_abs > 0:
            combined_noise /= max_abs

        # Scale the noise by 32767 and convert to int16
        combined_noise_scaled = (combined_noise * 32767).astype(np.int16)

        # Write the combined noise to a WAV file
        file_path = f"{self.selected_directory}/noise_{seed_for_filename}_combined.wav"
        wavfile.write(file_path, 44100, combined_noise_scaled)

def main():
    root = tk.Tk()
    root.iconbitmap('anw-ico.ico')
    app = NoiseGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()

