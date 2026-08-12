import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const solutions = defineCollection({
  loader: glob({
    pattern: "FE-*.md",
    base: "../solutions",
    generateId: ({ entry }) => entry.replace(/\.md$/, ""),
  }),

  schema: z.object({
    status: z.enum(["open", "solved"]),
    authors: z.array(z.string()).default([]),
    verified_by: z.array(z.string()).default([]),
    date_resolved: z.string().nullable().optional(),
    tags: z.array(z.string()).default([]),
  }),
});

export const collections = { solutions };