CREATE TABLE `clients` (
	`id` text PRIMARY KEY NOT NULL,
	`owner_id` text NOT NULL,
	`name` text NOT NULL,
	`company` text,
	`email` text,
	`phone` text,
	`notes` text,
	`version` integer DEFAULT 1 NOT NULL,
	`created_at` integer NOT NULL,
	`updated_at` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `clients_owner_idx` ON `clients` (`owner_id`);--> statement-breakpoint
CREATE UNIQUE INDEX `clients_owner_email_uq` ON `clients` (`owner_id`,`email`);--> statement-breakpoint
CREATE TABLE `invoices` (
	`id` text PRIMARY KEY NOT NULL,
	`client_id` text NOT NULL,
	`invoice_number` text NOT NULL,
	`status` text DEFAULT 'draft' NOT NULL,
	`issued_at` integer,
	`due_at` integer,
	`total_cents` integer DEFAULT 0 NOT NULL,
	`created_at` integer NOT NULL,
	FOREIGN KEY (`client_id`) REFERENCES `clients`(`id`) ON UPDATE no action ON DELETE restrict,
	CONSTRAINT "invoices_status_chk" CHECK("invoices"."status" in ('draft','sent','paid','void'))
);
--> statement-breakpoint
CREATE UNIQUE INDEX `invoices_invoice_number_unique` ON `invoices` (`invoice_number`);--> statement-breakpoint
CREATE INDEX `invoices_client_idx` ON `invoices` (`client_id`);--> statement-breakpoint
CREATE INDEX `invoices_status_idx` ON `invoices` (`status`);--> statement-breakpoint
CREATE TABLE `projects` (
	`id` text PRIMARY KEY NOT NULL,
	`client_id` text NOT NULL,
	`name` text NOT NULL,
	`status` text DEFAULT 'active' NOT NULL,
	`budget_cents` integer,
	`hourly_rate_cents` integer NOT NULL,
	`created_at` integer NOT NULL,
	`updated_at` integer NOT NULL,
	FOREIGN KEY (`client_id`) REFERENCES `clients`(`id`) ON UPDATE no action ON DELETE restrict,
	CONSTRAINT "projects_status_chk" CHECK("projects"."status" in ('active','paused','completed','cancelled')),
	CONSTRAINT "projects_budget_chk" CHECK("projects"."budget_cents" is null or "projects"."budget_cents" >= 0),
	CONSTRAINT "projects_rate_chk" CHECK("projects"."hourly_rate_cents" >= 0)
);
--> statement-breakpoint
CREATE INDEX `projects_client_idx` ON `projects` (`client_id`);--> statement-breakpoint
CREATE INDEX `projects_status_idx` ON `projects` (`status`);--> statement-breakpoint
CREATE TABLE `time_entries` (
	`id` text PRIMARY KEY NOT NULL,
	`project_id` text NOT NULL,
	`invoice_id` text,
	`description` text,
	`started_at` integer NOT NULL,
	`minutes` integer NOT NULL,
	`created_at` integer NOT NULL,
	FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`invoice_id`) REFERENCES `invoices`(`id`) ON UPDATE no action ON DELETE set null,
	CONSTRAINT "time_entries_minutes_chk" CHECK("time_entries"."minutes" > 0)
);
--> statement-breakpoint
CREATE INDEX `time_entries_project_started_idx` ON `time_entries` (`project_id`,`started_at`);--> statement-breakpoint
CREATE INDEX `time_entries_invoice_idx` ON `time_entries` (`invoice_id`);