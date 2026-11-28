import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  CheckCircle2,
  Circle,
  Plus,
  Trash2,
  ShoppingCart,
  ArrowRight,
  AlertCircle,
} from "lucide-react";
import {
  api,
  errorText,
  STANDARD_UNITS,
  type GroceryItem,
  type GroceryList,
} from "../services/api";

const AISLE_ORDER = [
  "Produce",
  "Meat & Seafood",
  "Dairy & Refrigerated",
  "Pantry & Baking",
  "Other",
];

export function GroceryPage() {
  const [list, setList] = useState<GroceryList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Quick manual add form state
  const [name, setName] = useState("");
  const [amount, setAmount] = useState<number | "">(1);
  const [unit, setUnit] = useState<string>("count");
  const [department, setDepartment] = useState<string>("Other");
  const [isAdding, setIsAdding] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .getGroceryList()
      .then((data) => {
        if (active) {
          setList(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (active) {
          setError(errorText(err));
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleToggleCheck(item: GroceryItem) {
    if (!list) return;
    const newChecked = !item.is_checked;

    // Optimistic update
    setList({
      ...list,
      items: list.items.map((i) =>
        i.id === item.id ? { ...i, is_checked: newChecked } : i
      ),
    });

    try {
      await api.updateGroceryItem(item.id, { is_checked: newChecked });
    } catch (err) {
      // Revert on failure
      setList({
        ...list,
        items: list.items.map((i) =>
          i.id === item.id ? { ...i, is_checked: item.is_checked } : i
        ),
      });
      setError(errorText(err));
    }
  }

  async function handleDeleteItem(itemId: number) {
    if (!list) return;
    const previousItems = list.items;

    // Optimistic delete
    setList({
      ...list,
      items: list.items.filter((i) => i.id !== itemId),
    });

    try {
      await api.deleteGroceryItem(itemId);
    } catch (err) {
      setList({ ...list, items: previousItems });
      setError(errorText(err));
    }
  }

  async function handleAddItem(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || amount === "" || Number(amount) <= 0 || !list) return;

    setIsAdding(true);
    setError(null);

    try {
      const newItem = await api.addGroceryItem({
        name: name.trim(),
        amount: Number(amount),
        unit: unit.trim() || "count",
        department: department.trim() || "Other",
      });
      setList({
        ...list,
        items: [...list.items, newItem],
      });
      setName("");
      setAmount(1);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setIsAdding(false);
    }
  }

  if (loading) {
    return (
      <div className="py-12 text-center text-slate-500">
        <p>Loading your grocery checklist…</p>
      </div>
    );
  }

  const items = list?.items || [];
  const completedCount = items.filter((i) => i.is_checked).length;
  const progressPercent = items.length > 0 ? Math.round((completedCount / items.length) * 100) : 0;

  // Group items by aisle department
  const groupedItems = AISLE_ORDER.reduce<Record<string, GroceryItem[]>>((acc, dept) => {
    acc[dept] = items.filter((i) => (i.department || "Other") === dept);
    return acc;
  }, {});

  // Group any other department not in standard list
  const otherItems = items.filter(
    (i) => !AISLE_ORDER.includes(i.department || "Other")
  );
  if (otherItems.length > 0) {
    groupedItems["Other"] = [...(groupedItems["Other"] || []), ...otherItems];
  }

  return (
    <div className="max-w-3xl mx-auto py-6 px-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <ShoppingCart className="w-6 h-6 text-amber-600" />
            <h1 className="text-2xl font-bold text-slate-900">
              {list?.title || "My Grocery List"}
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Aggregated shopping checklist sorted by supermarket aisle
          </p>
        </div>

        {items.length > 0 && (
          <div className="text-right">
            <span className="text-sm font-semibold text-slate-700">
              {completedCount} of {items.length} items purchased ({progressPercent}%)
            </span>
            <div className="w-48 h-2 bg-slate-200 rounded-full mt-1.5 overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {error && (
        <div
          role="alert"
          className="p-3 text-sm rounded-lg bg-rose-50 border border-rose-200 text-rose-700 flex items-center gap-2"
        >
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Manual Quick Add Item Form */}
      <form
        onSubmit={handleAddItem}
        className="card p-3 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-wrap items-center gap-2"
      >
        <input
          type="text"
          placeholder="Add item (e.g. eggs, almond milk)..."
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="flex-1 min-w-[160px] px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
          required
        />
        <input
          type="number"
          step="any"
          min="0.01"
          placeholder="Qty"
          value={amount}
          onChange={(e) => setAmount(e.target.value === "" ? "" : Number(e.target.value))}
          className="w-20 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
          required
        />
        <select
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
          className="px-2 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          {STANDARD_UNITS.map((u) => (
            <option key={u} value={u}>
              {u}
            </option>
          ))}
        </select>
        <select
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          className="px-2 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          {AISLE_ORDER.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
        <button
          type="submit"
          disabled={!name.trim() || amount === "" || isAdding}
          className="px-4 py-2 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg flex items-center gap-1 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add</span>
        </button>
      </form>

      {/* Empty State */}
      {items.length === 0 ? (
        <div className="card py-12 px-6 text-center border border-dashed border-slate-300 rounded-xl bg-slate-50/50">
          <ShoppingCart className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-800">Your grocery checklist is empty</h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1 mb-5">
            Add items manually using the bar above, or select recipes to aggregate ingredients automatically.
          </p>
          <Link
            to="/recipes"
            className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium rounded-lg transition-colors"
          >
            <span>Explore Recipes</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        /* Department Aisle Sections */
        <div className="space-y-6">
          {AISLE_ORDER.map((dept) => {
            const deptItems = groupedItems[dept] || [];
            if (deptItems.length === 0) return null;

            return (
              <section key={dept} className="card p-4 bg-white border border-slate-200 rounded-xl shadow-sm">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-3">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-amber-800">
                    {dept} ({deptItems.length})
                  </h2>
                </div>

                <ul className="divide-y divide-slate-100">
                  {deptItems.map((item) => (
                    <li
                      key={item.id}
                      className="py-2.5 flex items-center justify-between gap-3 group hover:bg-slate-50/50 px-2 rounded-lg transition-colors"
                    >
                      <button
                        type="button"
                        onClick={() => handleToggleCheck(item)}
                        className="flex items-center gap-3 text-left flex-1 min-w-0"
                      >
                        {item.is_checked ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                        ) : (
                          <Circle className="w-5 h-5 text-slate-300 group-hover:text-amber-500 flex-shrink-0" />
                        )}
                        <span
                          className={`text-sm ${
                            item.is_checked
                              ? "line-through text-slate-400 font-normal"
                              : "text-slate-900 font-medium"
                          }`}
                        >
                          <span className="font-semibold">
                            {item.amount} {item.unit !== "count" && item.unit}
                          </span>{" "}
                          {item.name}
                        </span>
                      </button>

                      <button
                        type="button"
                        aria-label={`Delete ${item.name}`}
                        onClick={() => handleDeleteItem(item.id)}
                        className="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-rose-600 rounded-md hover:bg-rose-50 transition-all"
                        title="Remove item"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </li>
                  ))}
                </ul>
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}
