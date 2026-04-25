import numpy as np

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]

def get_observed():
    print("Enter OBSERVED colors:")
    colors = []
    for i in range(3):
        h = input(f"Color {i+1} (hex, e.g. #3B434F): ")
        colors.append(hex_to_rgb(h))
    return np.array(colors).T  # columns = samples

def main():
    observed = get_observed()

    """ MOTOR:
    observed = np.array([
        [86, 70, 38],
        [51, 92, 62],
        [47, 85, 63],
    ])
    """
    """
    observed = np.array([
        [135, 74, 45],
        [63, 81, 51],
        [59, 67, 79],
    ])
    """
    # Hardcoded expected values (columns = samples)
    expected = np.array([
        [175, 54, 60],
        [70, 148, 73],
        [56, 61, 150],
    ])

    
    transform = np.linalg.inv(expected)
    coef = transform @ observed

    print(np.round(coef, 4))

    name = input("Enter output file name: ")
    if not name:
        print("Invalid name.")
        return

    filename = f"{name}.txt"

    with open(filename, "w") as f:
        for row in coef:
            f.write(" ".join(f"{val:.4f}" for val in row) + "\n")

    print(f"Matrix written to {filename}")

if __name__ == "__main__":
    main()