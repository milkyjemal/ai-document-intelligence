import * as React from "react";

type Props = {
  title: string;
  tone?: "warning" | "danger";
  items: string[];
};

export function AlertList({ title, tone = "warning", items }: Props) {
  if (!items.length) return null;

  const wrapper =
    tone === "danger"
      ? "border-rose-200 bg-rose-50 text-rose-950 dark:border-rose-950/60 dark:bg-rose-950/30 dark:text-rose-100"
      : "border-amber-200 bg-amber-50 text-amber-950 dark:border-amber-950/60 dark:bg-amber-950/30 dark:text-amber-100";

  return (
    <section className={`rounded-2xl border p-4 ${wrapper}`}>
      <h3 className="text-sm font-semibold">{title}</h3>
      <ul className="mt-2 list-disc pl-5 text-sm leading-6">
        {items.map((x, i) => (
          <li key={`${i}-${x}`}>{x}</li>
        ))}
      </ul>
    </section>
  );
}
