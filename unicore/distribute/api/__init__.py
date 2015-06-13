from pyramid.config import Configurator

from unicore.distribute.api import proxy


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('unicore.distribute.api')
    return config.make_wsgi_app()


def includeme(config):
    config.include('cornice')
    config.scan('.repos')

    settings = config.registry.settings
    proxy_enabled = settings.get('proxy.enabled', 'false').lower()
    proxy_path = settings.get('proxy.path', 'esapi')
    proxy_upstream = settings.get('proxy.upstream', 'http://localhost:9200/')

    if proxy_enabled == 'true':  # pragma: no cover
        config.add_route('esapi', '/%s/{parts:.*}' % (proxy_path,))
        config.add_view(proxy.Proxy(proxy_upstream), route_name='esapi')

    indexing_enabled = settings.get('es.indexing_enabled', 'false').lower()
    if indexing_enabled == 'true':
        config.add_subscriber(
            'unicore.distribute.api.repos.initialize_repo_index',
            'unicore.distribute.events.RepositoryCloned')
        config.add_subscriber(
            'unicore.distribute.api.repos.update_repo_index',
            'unicore.distribute.events.RepositoryUpdated')
        config.add_subscriber(
            'unicore.distribute.api.repos.index_content_type_object',
            'unicore.distribute.events.ContentTypeObjectUpdated')
        config.add_subscriber(
            'unicore.distribute.api.repos.unindex_content_type_object',
            'unicore.distribute.events.ContentTypeObjectDeleted')
