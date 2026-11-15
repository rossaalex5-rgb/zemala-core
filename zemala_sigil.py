import hashlib
import numpy as np
import matplotlib.pyplot as plt

def generate_zemala_sigil(seed_text: str, contract_verified: bool = False, save_path: str = None):
    hash_hex = hashlib.sha256(seed_text.encode('utf-8')).hexdigest()
    hash_bytes = bytes.fromhex(hash_hex)
    
    extended_bytes = bytearray()
    counter = 0
    while len(extended_bytes) < 121:
        chunk = hashlib.sha256(hash_bytes + counter.to_bytes(4, 'big')).digest()
        extended_bytes.extend(chunk)
        counter += 1
    extended_bytes = extended_bytes[:121]

    grid_size = 11
    voxels = np.zeros((grid_size, grid_size, 5), dtype=bool)
    colors = np.empty(voxels.shape, dtype=object)

    relation_colors = {
        0: '#D9383A',
        1: '#2EA043',
        2: '#1F6FEB',
        3: '#E3B341'
    }
    gold_color = '#FFD700'

    for idx in range(121):
        x = idx % grid_size
        y = idx // grid_size
        byte_val = extended_bytes[idx]

        if contract_verified:
            height = 1
            color = gold_color
        else:
            height = (byte_val % 4) + 1
            color_code = (byte_val >> 2) % 4
            color = relation_colors[color_code]

        voxels[x, y, :height] = True
        colors[x, y, :height] = color

    fig = plt.figure(figsize=(10, 8), facecolor='#0D1117')
    ax = fig.add_subplot(111, projection='3d', facecolor='#0D1117')

    ax.voxels(voxels, facecolors=colors, edgecolor='#161B22', linewidth=0.6)
    
    # Exaktes Seitenverhaeltnis erzwingen (flache 11x11 Platte statt hohem Wuerfel)
    ax.set_box_aspect((11, 11, 3.5))
    ax.set_zlim(0, 5)
    
    ax.set_axis_off()
    ax.view_init(elev=35, azim=45)

    status_text = "CONTRACT VERIFIZIERT - ZUSTAND: GOLD" if contract_verified else "11x11 SIGIL - AUSGANGSZUSTAND (UNGEPRUEFT)"
    plt.suptitle(f"ZEMALA CORE V2.3 | {status_text}", color='white', fontsize=14, fontweight='bold', y=0.94)
    plt.title(f"SHA-256: {hash_hex}", color='#8B949E', fontsize=9, family='monospace', pad=10)

    if contract_verified:
        legend_text = "GOLD = Funktionierend, stabil, Contract eingehalten (AEVO-konform)"
    else:
        legend_text = "Rot = Herkunft   Gruen = Widerspruch   Blau = Bestaetigung   Gelb = Kausalitaet"
    
    fig.text(0.5, 0.05, legend_text, ha='center', color='#C9D1D9', fontsize=10)

    if save_path:
        plt.savefig(save_path, dpi=200, facecolor='#0D1117')
        print(f"Gespeichert unter: {save_path}")
    else:
        plt.show()

if __name__ == "__main__":
    test_seed = "Komponente ist bei allen Teilnehmern vorhanden und Flaschenhals ist entfernt."
    generate_zemala_sigil(test_seed, contract_verified=False, save_path="sigil_ungeprueft.png")
    generate_zemala_sigil(test_seed, contract_verified=True, save_path="sigil_gold.png")
