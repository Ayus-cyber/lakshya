import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_er_diagram():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Styles
    header_color = "#4da6ff" # Light Blue
    body_color = "#f0f5f5"   # Very Light Grey
    edge_color = "#003366"   # Dark Blue
    text_color = "#000000"
    
    # Entity Definitions: (x, y, width, height)
    # Origin is bottom-left
    entities = {
        "Products": {
            "pos": (10, 75), "size": (20, 18), 
            "cols": ["PK product_id", "product_name", "category", "unit_price"]
        },
        "Stores": {
            "pos": (70, 75), "size": (20, 15), 
            "cols": ["PK store_id", "store_name", "city"]
        },
        # Transactional
        "Inventory_Snapshot": {
            "pos": (10, 25), "size": (22, 18), 
            "cols": ["date", "FK store_id", "FK product_id", "quantity"]
        },
        "Restock_Events": {
            "pos": (70, 25), "size": (22, 18), 
            "cols": ["event_date", "FK store_id", "FK product_id", "restock_qty"]
        },
        # Derived
        "Inventory_Fact": {
            "pos": (40, 50), "size": (22, 15), 
            "cols": ["FK store_id", "FK product_id", "effective_stock"]
        }
    }

    def draw_entity(name, data):
        x, y = data['pos']
        w, h = data['size']
        cols = data['cols']
        
        # Header Box
        header_h = 4
        rect_header = patches.Rectangle((x, y + h - header_h), w, header_h, 
                                      linewidth=1.5, edgecolor=edge_color, facecolor=header_color)
        ax.add_patch(rect_header)
        ax.text(x + w/2, y + h - header_h/2 - 0.5, name, ha='center', fontsize=10, weight='bold', color='white')
        
        # Body Box
        body_h = h - header_h
        rect_body = patches.Rectangle((x, y), w, body_h, 
                                    linewidth=1.5, edgecolor=edge_color, facecolor=body_color)
        ax.add_patch(rect_body)
        
        # Column Text
        current_y = y + body_h - 3
        for col in cols:
            prefix = ""
            if "PK" in col: prefix = "🔑 "
            elif "FK" in col: prefix = "🔗 "
            
            clean_col = col.replace("PK ", "").replace("FK ", "")
            
            ax.text(x + 1, current_y, f"{prefix}{clean_col}", fontsize=9, color=text_color)
            current_y -= 2.5

    # Draw all entities
    for name, data in entities.items():
        draw_entity(name, data)

    # Connections with Notation
    # Helper to draw line with text at ends
    def connect(ent1, ent2, label1, label2):
        d1 = entities[ent1]
        d2 = entities[ent2]
        
        # Center points
        x1 = d1['pos'][0] + d1['size'][0]/2
        y1 = d1['pos'][1] + d1['size'][1]/2
        
        x2 = d2['pos'][0] + d2['size'][0]/2
        y2 = d2['pos'][1] + d2['size'][1]/2
        
        # Simple straight line for now (imperfect but functional)
        # Choosing anchor points based on relative position
        if y1 > y2: # 1 is above 2
            p1 = (x1, d1['pos'][1]) # Bottom of 1
            p2 = (x2, d2['pos'][1] + d2['size'][1]) # Top of 2
        else:
            p1 = (x1, d1['pos'][1] + d1['size'][1])
            p2 = (x2, d2['pos'][1])
            
        # If x is far apart, maybe connect sides?
        # Let's keep it simple: vertical connections primarily or diagonal
        
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#555555', linestyle='-', linewidth=1.5, zorder=0)
        
        # Add labels
        # Interpolate a bit inward to place text
        ax.text(p1[0], p1[1] + (1 if y1 < y2 else -2), label1, ha='center', fontsize=10, weight='bold', color='red', backgroundcolor='white')
        ax.text(p2[0], p2[1] + (-2 if y1 < y2 else 1), label2, ha='center', fontsize=10, weight='bold', color='red', backgroundcolor='white')

    # Relationships
    # Products (1) -- (N) Inventory_Snapshot
    # We need to explicitly define connection points to avoid overlapping lines
    
    # 1. Products to Snapshot (Left Side Vertical)
    connect("Products", "Inventory_Snapshot", "1", "N")
    
    # 2. Stores to Restock (Right Side Vertical)
    connect("Stores", "Restock_Events", "1", "N")
    
    # 3. Stores to Snapshot (Cross? Let's assume Stores is also linked to Snapshot)
    # Stores (1) -- (N) Snapshot
    # Draw line from Store Bottom-Left to Snapshot Top-Right?
    # Trying to keep it clean.
    # Manual line for Stores -> Snapshot
    p_store_left = (70, 80)
    p_snap_right = (32, 35)
    # ax.plot([70, 32], [80, 43], color='grey', linestyle=':') 
    # Skipping cross lines to keep diagram clean, focusing on primary flow or Fact Table
    
    # 4. Products to Fact (Center)
    connect("Products", "Inventory_Fact", "1", "N")
    
    # 5. Stores to Fact (Center)
    connect("Stores", "Inventory_Fact", "1", "N")
    
    # Title
    ax.text(50, 96, "Retail Operational Intelligence - ER Schema", ha='center', fontsize=18, weight='bold')
    ax.text(50, 2, "1 : N  = One to Many Relationship", ha='center', fontsize=10, style='italic')

    output_path = r"C:/Users/91823/.gemini/antigravity/brain/8f155d49-b9ca-49ba-bcb8-3c7db8ff8b32/ER_Diagram_Detailed.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Diagram saved to: {output_path}")

if __name__ == "__main__":
    draw_er_diagram()
