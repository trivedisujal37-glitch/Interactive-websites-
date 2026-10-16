# Supply Chain Optimization System

Interactive web application for supply chain analytics, inventory monitoring, demand forecasting, supplier performance tracking, cost analysis, and human-in-the-loop optimization recommendations. Built with Python and Streamlit.

---

## Getting Started

### 1. Installation
Install project dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run Application
Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```

### 3. Run Test Suite
Execute the automated test suite with pytest:
```bash
pytest
```

---

## Supported Column Schema

The application includes a centralized canonical column resolver (`utils/columns.py`) supporting flexible header variations across `.csv` and `.xlsx` files without case-sensitive errors or substring guessing:

| Canonical Key | Supported Variations / Aliases |
| :--- | :--- |
| `item_id` | `item_id`, `itemid`, `item`, `sku`, `product`, `productid` |
| `item_name` | `item_name`, `itemname`, `product_name`, `productname` |
| `date` | `date`, `order_date`, `transaction_date`, `day` |
| `demand` | `demand`, `quantity_demanded`, `quantitydemanded`, `quantity_sold`, `quantitysold`, `sales`, `usage` |
| `current_stock` | `current_stock`, `currentstock`, `stock`, `on_hand`, `onhand`, `inventory` |
| `reorder_point` | `reorder_point`, `reorderpoint`, `rop`, `reorder_level` |
| `max_stock` | `max_stock`, `maxstock`, `max_stock_level`, `maxstocklevel` |
| `unit_price` | `unit_price`, `unitprice`, `price` |
| `supplier_id` | `supplier_id`, `supplierid`, `supplier`, `vendor_id`, `vendor` |
| `delivery_time` | `delivery_time`, `deliverytime`, `lead_time`, `leadtime`, `lead_days`, `leaddays` |
| `quantity_supplied` | `quantity_supplied`, `quantitysupplied`, `qty_supplied`, `qtysupplied`, `received` |
| `supplier_unit_price` | `supplier_unit_price`, `supplierunitprice`, `vendor_price` |
| `transportation_cost`| `transportation_cost`, `transportationcost`, `freight`, `shipping_cost` |
| `holding_cost` | `holding_cost`, `holdingcost`, `carrying_cost` |
| `purchase_cost` | `purchase_cost`, `purchasecost` |
| `category` | `category`, `item_category`, `itemcategory`, `product_category`, `productcategory` |

---

## Core Calculations & Formulas

- **Reorder Point (ROP)**:
  $$\text{Reorder Point} = (\text{Average Demand} \times \text{Lead Time}) + \text{Safety Stock}$$
  $$\text{Safety Stock} = 1.65 \times \sigma_{\text{demand}} \times \sqrt{\text{Lead Time}}$$
  *If lead time is unavailable, Reorder Point is left blank and status is marked "Lead time unavailable - review".*
- **Cost Analysis**:
  $$\text{Total Combined Cost} = \text{Purchase Cost} + \text{Holding Cost} + \text{Transportation Cost}$$
  *Unit Price is an intensive rate, not an expenditure, and is analyzed separately as Average Unit Price.*
- **Demand Forecasting**:
  Simple Moving Average ($\text{window} = 3$) with chronological 80/20 train/test evaluation.

### Inventory Status Note
In datasets such as `data/supply_chain_sample_data.csv`, a large majority of rows (1,368 of 1,456) receive the "Overstock" status. This is an inherent property of the dataset's scale, not a calculation bug:
- Median Current Stock is 415.0 units, while median average demand is 12.02 units/day and median lead time is 3.85 days.
- The resulting median Reorder Point is 58.57 units.
- Under the status threshold `stock gap > (reorder point * 2) + 1` (i.e. `Current Stock > 3 * ROP + 1` ≈ 176.7 units), on-hand stock (median 415 units, or ~35 days of buffer against a ~3.8-day lead time) substantially exceeds reorder thresholds and is legitimately categorized as Overstock.

---

## Limitations

1. **Forecast Horizon**: The Simple Moving Average (window=3) operates on the aggregate daily demand series across all items; multi-step recursive rolling averages flatten asymptotically toward the series mean.
2. **Stateless Operations**: Datasets are loaded in memory via Streamlit session state; no persistent external database is attached.
3. **Decision Support Only**: Optimization findings and recommendations highlight observational thresholds (e.g. stock below reorder point or exceeding maximum level); human approval is explicitly required before taking operational action.
