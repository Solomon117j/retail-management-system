HTMX Modernization Guide
=======================

This document scans the current codebase for existing HTMX usage and provides a practical guide, examples, and a phased roadmap to modernize the UI with HTMX. It focuses on progressive enhancement, small iterative changes, and safe server-side patterns for Django.

Summary of scan
---------------
- HTMX script: included in `templates/base.html` (already present in the project).
- HTMX fragment: `templates/htmx/counter_fragment.html` — a working demo fragment with a button using `hx-get`.
- Dashboard: `templates/dashboard/index.html` now includes the counter fragment (`{% include 'htmx/counter_fragment.html' %}`) so a minimal demo is embedded.
- HTMX endpoint: `dashboards.views.htmx_counter` returns the fragment and stores a small counter in the session.

Goals for HTMX modernization
----------------------------
- Improve perceived performance by replacing full-page reloads with fragment swaps.
- Reduce complex front-end JS by using HTMX declarative attributes.
- Keep server-side logic in Django views and templates (progressive enhancement).
- Introduce small, reversible changes and measure impact.

Quick start (what's already done)
---------------------------------
1. HTMX script is included in `templates/base.html` via CDN.
2. Demo HTMX fragment exists and is embedded in the dashboard.

If you don't already have HTMX included, add in `base.html` just before other scripts:

```html
<script src="https://unpkg.com/htmx.org@1.10.0"></script>
```

CSRF and HTMX (required)
-------------------------
Django requires the `X-CSRFToken` header for POST/unsafe requests. Add a small config to the base template to attach the CSRF token to all HTMX requests.

Option A — add listener using cookie `csrftoken` (works with default Django settings):

```html
<script>
  document.body.addEventListener('htmx:configRequest', (event) => {
    const cookie = document.cookie.match(/(^|;)\s*csrftoken=([^;]+)/);
    if (cookie) {
      event.detail.headers['X-CSRFToken'] = cookie[2];
    }
  });
</script>
```

Option B — inline header on a per-element basis (example):

```html
<button hx-post="/some/endpoint/" hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>Submit</button>
```

Server-side detection of HTMX requests
-------------------------------------
Use the `HX-Request` header to detect HTMX requests and return fragments when appropriate.

Example view pattern:

```python
from django.shortcuts import render

def my_view(request):
    context = {...}
    if request.headers.get('HX-Request'):
        return render(request, 'partials/my_fragment.html', context)
    return render(request, 'full_pages/my_page.html', context)
```

Patterns and examples
---------------------
1) Pagination / List updates
- Convert an existing list view into a server-rendered list + partial for pagination controls.
- Return a fragment when HX request detected, full page otherwise.

View example (simplified):

```python
from django.core.paginator import Paginator
from django.shortcuts import render

def product_list(request):
    qs = Product.objects.all().order_by('-id')
    paginator = Paginator(qs, 20)
    page = request.GET.get('page', 1)
    items = paginator.get_page(page)
    ctx = {'items': items}
    if request.headers.get('HX-Request'):
        return render(request, 'inventory/product_list_fragment.html', ctx)
    return render(request, 'inventory/product_list.html', ctx)
```

Template usage (partial):

```html
<!-- inventory/product_list_fragment.html -->
<div id="product-list">
  {% for p in items %}
    <div class="product-row">{{ p.name }}</div>
  {% endfor %}
  <nav>
    {% if items.has_previous %}
      <a hx-get="?page={{ items.previous_page_number }}" hx-target="#product-list" hx-swap="outerHTML">Prev</a>
    {% endif %}
    {% if items.has_next %}
      <a hx-get="?page={{ items.next_page_number }}" hx-target="#product-list" hx-swap="outerHTML">Next</a>
    {% endif %}
  </nav>
</div>
```

2) Inline edit forms & modals
- Use `hx-get` to fetch a form fragment and `hx-post` to submit.
- Return the updated row fragment on success (or the form with errors on failure).

Example button to open a modal (on the page):

```html
<button hx-get="{% url 'inventory:product_edit' product.id %}" hx-target="#modal-body" hx-swap="innerHTML">Edit</button>
```

Server returns a partial which contains the form HTML. The submit button on that form can use `hx-post` and on success replace the row with the returned fragment.

3) Out-of-band updates (OOB)
- Use `hx-swap-oob` with HTMX to update multiple parts of the page from a single response (e.g., update a navigation counter and the list item simultaneously).

Example response fragment:

```html
<div hx-swap-oob="true" id="cart-count">{{ cart_count }}</div>
<div id="row-123">...updated row...</div>
```

4) Push notifications & realtime
- For low-throughput real-time, use HTMX with Server-Sent Events (SSE) or integrate Django Channels for WebSockets.
- HTMX has extensions for SSE; SSE endpoints must be long-lived and served by an ASGI server.

Security & permissions
----------------------
- Continue to perform all permission checks server-side regardless of HTMX.
- Never rely on client-sent flags to determine visibility or privileged actions.
- Sanitize and validate all inputs as usual.
- Protect endpoints that return fragments with `login_required` and any `UserPassesTestMixin` checks as appropriate.

Accessibility
-------------
- Manage focus after fragment swaps: set `autofocus` on replaceable inputs or add JS listeners for `htmx:afterSwap` to set focus.
- Add appropriate `role` and `aria-*` attributes to modal content and interactive controls.

Testing & CI
------------
- Add unit tests for view behavior: verify that an HX request returns the fragment template and a normal request returns the full page.
- Use Selenium / Playwright / Playwright for Django to validate end-to-end interactive behavior (button click updates without full-page reload).
- Add snapshot tests for partials if you maintain consistent markup.

Rollout plan (small -> big)
---------------------------
1. Keep HTMX in `base.html` (done).
2. Small experiment: product list pagination or dashboard widget (already have a counter demo). Measure feedback.
3. Convert a single form flow (e.g., Add/Edit Product) to HTMX modal pattern.
4. Inline editable rows for frequently updated resources (stock counts, prices).
5. Live notifications or small realtime panels (using SSE/Channels if needed).
6. Expand to other admin pages and customer-facing pages conservatively.

Potential integration points discovered (recommended first targets)
------------------------------------------------------------------
- `inventory/product_list.html` and `inventory/product_list` view — add HTMX pagination/filters.
- `templates/dashboard/index.html` — expand widgets to update via HTMX (e.g., inventory count, new orders list).
- E-commerce checkout flows — small fragments for shipping/payment steps to speed flow.
- Modal-based create/edit forms across `store_management`, `procurement`, `hr` apps.

Developer checklist for each conversion
---------------------------------------
- [ ] Add a fragment template under `templates/partials/` or `templates/htmx/`.
- [ ] Update view to detect `HX-Request` and return fragment where appropriate.
- [ ] Use `hx-get`/`hx-post` on triggers and set `hx-target`/`hx-swap` appropriately.
- [ ] Ensure CSRF header is supplied for POSTs (see CSRF section).
- [ ] Add server-side permission checks and tests.
- [ ] Add accessibility focus management (use `htmx:afterSwap` event).

Example: Convert a simple form submit to HTMX
--------------------------------------------
Template (trigger):

```html
<form hx-post="{% url 'sales:customer_create' %}" hx-target="#create-result" hx-swap="innerHTML">
  {% csrf_token %}
  <!-- fields -->
  <button type="submit">Create</button>
</form>
<div id="create-result"></div>
```

View (Django):

```python
from django.shortcuts import render, redirect
from .forms import CustomerForm

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            obj = form.save()
            # On HTMX, return a small confirmation fragment
            if request.headers.get('HX-Request'):
                return render(request, 'partials/customer_created_fragment.html', {'customer': obj})
            return redirect('sales:customer_list')
    else:
        form = CustomerForm()
    if request.headers.get('HX-Request'):
        return render(request, 'partials/customer_form_fragment.html', {'form': form})
    return render(request, 'sales/customer_create.html', {'form': form})
```

Deployment & Docker notes
-------------------------
- HTMX is client-side only (small JS), so it doesn't change the Python build significantly.
- If you vendor HTMX (for offline or lock-step release), add it to your static pipeline and `collectstatic`.
- Ensure any long-lived SSE endpoints run under an ASGI server in production (Daphne/Uvicorn + Channels) — the WSGI server will not handle SSE/WS correctly.

Observability & metrics
-----------------------
- Add logging around HTMX endpoints to track latency and error rates.
- Use browser RUM or synthetic checks to measure perceived latency improvements.

Common pitfalls & how to avoid them
----------------------------------
- Forgetting CSRF headers — fix with a small config listener in `base.html`.
- Returning full pages for HX requests — be explicit and return fragments to avoid unexpected HTML duplication.
- Not checking permissions server-side — continue to protect views as always.
- Complex client-side state that assumes full-page reloads — port local state carefully (prefer server-driven state when possible).

Next steps I can do for you
---------------------------
- Convert `inventory/product_list` to HTMX-powered pagination (implement view + fragments + template changes + tests).
- Convert a modal-based edit flow (pick an entity: Product, Store, Supplier) and demo the pattern.
- Add a short automated integration test (Playwright or Selenium) that clicks the HTMX demo button and asserts DOM change.
- Harden CSRF handling in `base.html` (add the `htmx:configRequest` snippet) and add a small utility partial folder.

Files I found during scan
-------------------------
- `templates/base.html` — HTMX script location.
- `templates/htmx/counter_fragment.html` — demo fragment.
- `templates/dashboard/index.html` — includes the demo fragment.
- `dashboards/views.py` — contains `htmx_counter` and dashboard views.

Contact / ownership
-------------------
If you want, tell me which first target (e.g., product list pagination, product edit modal) you prefer and I'll implement the full conversion with tests and a PR-ready commit.

---
Generated on: 2025-11-28
