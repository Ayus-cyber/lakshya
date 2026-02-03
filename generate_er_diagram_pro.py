import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_professional_er():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Professional Style Config
    styles = {
        'header_face': '#2c3e50', # Dark Slate
        'header_text': 'white',
        'body_face': '#ecf0f1',   # Light Gray
        'body_text': 'black',
        'border': '#34495e',
        'line_color': '#7f8c8d'   # Gray lines
    }

    # Entity Positions (Manually optimized for layout)
    # x, y, width, height
    entities = {
        "Products": {"x": 8, "y": 75, "w": 18, "h": 16, "cols": ["PK product_id", "product_name", "category", "unit_price"]},
        "Stores":   {"x": 74, "y": 75, "w": 18, "h": 14, "cols": ["PK store_id", "store_name", "city"]},
        
        "Inventory_Snapshot": {"x": 8, "y": 30, "w": 22, "h": 16, "cols": ["FK store_id", "FK product_id", "date", "quantity"]},
        "Restock_Events": {"x": 74, "y": 30, "w": 22, "h": 16, "cols": ["FK store_id", "FK product_id", "event_date", "restock_qty"]},
        
        "Inventory_Fact": {"x": 41, "y": 52, "w": 18, "h": 14, "cols": ["FK store_id", "FK product_id", "effective_stock"]}
    }

    # Helper: Draw Entity Table
    def draw_table(name, props):
        x, y, w, h = props['x'], props['y'], props['w'], props['h']
        
        # Shadow
        shadow = patches.Rectangle((x+0.5, y-0.5), w, h, facecolor='#bdc3c7', edgecolor='none', zorder=1)
        ax.add_patch(shadow)

        # Body Background
        body = patches.Rectangle((x, y), w, h, facecolor=styles['body_face'], edgecolor=styles['border'], linewidth=1.5, zorder=2)
        ax.add_patch(body)
        
        # Header Background
        header_h = 4
        header = patches.Rectangle((x, y + h - header_h), w, header_h, facecolor=styles['header_face'], edgecolor=styles['border'], linewidth=1.5, zorder=3)
        ax.add_patch(header)
        
        # Title
        ax.text(x + w/2, y + h - header_h/2 - 0.5, name, color=styles['header_text'], 
                ha='center', va='center', weight='bold', fontsize=11, zorder=4)

        # Columns
        col_start_y = y + h - header_h - 2.5
        for col in props['cols']:
            prefix = ""
            font_weight = 'normal'
            if "PK" in col:
                prefix = "PK  "
                font_weight = 'bold'
            elif "FK" in col:
                prefix = "FK  "
                font_weight = 'normal'
            
            clean_col = col.replace("PK ", "").replace("FK ", "")
            
            # Draw Key Type
            ax.text(x + 1, col_start_y, prefix, color=styles['border'], fontsize=8, weight='bold', zorder=4)
            # Draw Name
            ax.text(x + 3.5, col_start_y, clean_col, color=styles['body_text'], fontsize=9, weight=font_weight, zorder=4)
            col_start_y -= 2.2

    # Draw All Tables
    for name, props in entities.items():
        draw_table(name, props)

    # Helper: Draw Orthogonal Line with Crow's Foot
    def connect_orthogonal(ent1, ent2, start_side='bottom', end_side='top'):
        d1, d2 = entities[ent1], entities[ent2]
        
        # Start Point
        if start_side == 'bottom':
            xs, ys = d1['x'] + d1['w']/2, d1['y']
        elif start_side == 'right':
            xs, ys = d1['x'] + d1['w'], d1['y'] + d1['h']/2
        elif start_side == 'left':
            xs, ys = d1['x'], d1['y'] + d1['h']/2
            
        # End Point
        if end_side == 'top':
            xe, ye = d2['x'] + d2['w']/2, d2['y'] + d2['h']
        elif end_side == 'left':
            xe, ye = d2['x'], d2['y'] + d2['h']/2
        elif end_side == 'right':
            xe, ye = d2['x'] + d2['w'], d2['y'] + d2['h']/2

        # Wire Path (Midpoint Routing)
        mid_y = (ys + ye) / 2
        
        # Lines
        line_params = {'color': styles['line_color'], 'linewidth': 1.5, 'zorder': 0}
        
        if start_side == 'bottom' and end_side == 'top':
            # Vertical then Horizontal then Vertical
            ax.plot([xs, xs], [ys, mid_y], **line_params) # Down
            ax.plot([xs, xe], [mid_y, mid_y], **line_params) # Across
            ax.plot([xe, xe], [mid_y, ye], **line_params) # Down
            
            # Crow's Foot (at End/Bottom) - Actually checking direction
            # If entering top of child, Crow's foot is at (xe, ye) pointing UP? 
            # No, text standard: Crow's foot faces the Many side.
            # Assuming ent2 is the "Many" side.
            
            # Draw Crow's Foot at (xe, ye)
            # Three prongs pointing towards the line
            cf_size = 1.5
            # Center prong
            ax.plot([xe, xe], [ye, ye + cf_size], **line_params)
            # Left prong
            ax.plot([xe - cf_size, xe], [ye + cf_size, ye], **line_params)
            # Right prong
            ax.plot([xe + cf_size, xe], [ye + cf_size, ye], **line_params)
            
            # Optional: Circle for "Optional" or Bar for "Mandatory"
            # Draw mandatory bar
            ax.plot([xe - cf_size, xe + cf_size], [ye + cf_size, ye + cf_size], **line_params)

        elif start_side == 'right' and end_side == 'left':
             # Horizontal direct
             ax.plot([xs, xe], [ys, ye], **line_params)
             
             # Crow's foot at xe (Left facing)
             cf_size = 1.5
             ax.plot([xe, xe - cf_size], [ye, ye + cf_size], **line_params)
             ax.plot([xe, xe - cf_size], [ye, ye - cf_size], **line_params)
             ax.plot([xe - cf_size, xe - cf_size], [ye - cf_size, ye + cf_size], **line_params)


    # Connect Entities
    
    # 1. Products (1) -> Snapshots (N)
    connect_orthogonal("Products", "Inventory_Snapshot", 'bottom', 'top')
    
    # 2. Stores (1) -> Restocks (N)
    connect_orthogonal("Stores", "Restock_Events", 'bottom', 'top')
    
    # 3. Products (1) -> Fact (N)
    # Custom routing needed? Products is at (8, 75), Fact at (41, 52)
    # Let's go Right from Products, Top to Fact?
    # connect_orthogonal("Products", "Inventory_Fact", 'right', 'left') # Simple diagonal check
    # Let's use custom points
    p_prod = entities["Products"]
    p_fact = entities["Inventory_Fact"]
    
    # From Prod Right -> Fact Top
    start = (p_prod['x'] + p_prod['w'], p_prod['y'] + p_prod['h']/2)
    end = (p_fact['x'] + p_fact['w']/2, p_fact['y'] + p_fact['h'])
    
    ax.plot([start[0], end[0]], [start[1], start[1]], color=styles['line_color'], lw=1.5) # Across
    ax.plot([end[0], end[0]], [start[1], end[1]], color=styles['line_color'], lw=1.5) # Down
    
    # Crow's foot at Fact Top
    cf_x, cf_y = end
    cf_s = 1.5
    ax.plot([cf_x, cf_x - cf_s], [cf_y, cf_y + cf_s], color=styles['line_color'])
    ax.plot([cf_x, cf_x + cf_s], [cf_y, cf_y + cf_s], color=styles['line_color'])
    ax.text(end[0], start[1] + 1, "1 : N", fontsize=9, ha='right')

    # 4. Stores (1) -> Fact (N)
    p_store = entities["Stores"]
    start_s = (p_store['x'], p_store['y'] + p_store['h']/2)
    # End same as above? No, Fact has one top.
    # Enter Fact Right?
    end_f_right = (p_fact['x'] + p_fact['w'], p_fact['y'] + p_fact['h']/2)
    
    ax.plot([start_s[0], end_f_right[0]], [start_s[1], start_s[1]], color=styles['line_color'], lw=1.5) # Across Left to Match y
    # Actually Fact y is 52+7 = 59. Store y is 75+7 = 82.
    # Go Left from Store, Down to Fact Right?
    
    mid_x_sf = (start_s[0] + end_f_right[0]) / 2
    ax.plot([start_s[0], mid_x_sf], [start_s[1], start_s[1]], color=styles['line_color']) # Left
    ax.plot([mid_x_sf, mid_x_sf], [start_s[1], end_f_right[1]], color=styles['line_color']) # Down
    ax.plot([mid_x_sf, end_f_right[0]], [end_f_right[1], end_f_right[1]], color=styles['line_color']) # Left into Fact
    
    # Crow's foot at Fact Right
    # (Left facing)
    cf_x, cf_y = end_f_right
    ax.plot([cf_x, cf_x + cf_s], [cf_y, cf_y + cf_s], color=styles['line_color']) # Wrong direction
    # Pointing into box
    ax.plot([cf_x, cf_x + cf_s], [cf_y, cf_y + cf_s], color=styles['line_color']) 
    ax.plot([cf_x, cf_x + cf_s], [cf_y, cf_y - cf_s], color=styles['line_color'])

    # Title
    ax.text(50, 95, "Retail Operational Intelligence - Schema Diagram", ha='center', fontsize=20, weight='bold', color='#2c3e50')

    # Save
    output_path = r"C:/Users/91823/.gemini/antigravity/brain/8f155d49-b9ca-49ba-bcb8-3c7db8ff8b32/ER_Diagram_Professional.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Diagram saved to: {output_path}")

if __name__ == "__main__":
    draw_professional_er()
